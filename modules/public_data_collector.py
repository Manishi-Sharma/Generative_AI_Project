import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from config import STATUS_FOUND, STATUS_NOT_AVAILABLE, STATUS_RESTRICTED
from database.connection import SessionLocal
from database.models import FinancialData, Organisation
from integrations.sec_connector import SECConnector
from integrations.tavily_search import TavilySearchClient
from modules.data_extraction import DataExtractor
from modules.data_validation import DataValidator

logger = logging.getLogger(__name__)

class PublicDataCollector:
    """
    General-purpose public financial information collection engine.
    Discovers, verifies, and normalizes financial disclosures from SEC EDGAR,
    public investor reports, and credible web sources.
    """
    STANDARD_METRICS = [
        "Revenue",
        "Operating Expenses",
        "Operating Profit",
        "Net Profit",
        "Total Assets",
        "Total Liabilities",
        "Shareholders' Equity",
        "Cash and Cash Equivalents",
        "Borrowings (Debt)",
        "Operating Cash Flow",
        "Capital Expenditure",
        "Research & Development"
    ]

    def __init__(self):
        self.sec_connector = SECConnector()
        self.tavily_client = TavilySearchClient()

    def collect_organisation_financials(self, org: Organisation, cik: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes multi-source public financial collection for an organisation.
        """
        raw_records: List[Dict[str, Any]] = []

        # 1. Check if entity has SEC CIK or US ticker
        target_cik = cik
        if not target_cik and (org.ticker or org.name):
            sec_matches = self.sec_connector.find_company(org.ticker or org.name)
            if sec_matches:
                target_cik = sec_matches[0].get("cik")

        # 2. Extract from SEC EDGAR if CIK resolved
        if target_cik:
            logger.info(f"Querying SEC EDGAR facts for CIK {target_cik}")
            facts = self.sec_connector.get_company_facts(target_cik)
            if facts:
                sec_records = self.sec_connector.extract_standard_financials(facts)
                raw_records.extend(sec_records)

        # 3. Check Tavily for annual reports / financial disclosures
        if self.tavily_client.is_configured():
            logger.info(f"Searching Tavily for financial reports of {org.name}")
            tavily_results = self.tavily_client.search_financial_reports(org.name)
            for res in tavily_results:
                content = res.get("content", "")
                url = res.get("url", "")
                extracted = DataExtractor.extract_from_text(content, url, "Investor Relations Web Source")
                raw_records.extend(extracted)

        # 4. Supplementary public financial endpoint check (e.g. Yahoo Finance public quote summary if available)
        if org.ticker:
            try:
                yfin_url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{org.ticker}?modules=financialData,defaultKeyStatistics,cashflowStatementHistory"
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(yfin_url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json().get("quoteSummary", {}).get("result", [{}])[0]
                    fin = data.get("financialData", {})
                    # Total revenue
                    if "totalRevenue" in fin and fin["totalRevenue"].get("raw"):
                        raw_records.append({
                            "metric_name": "Revenue",
                            "value": float(fin["totalRevenue"]["raw"]),
                            "currency": "USD",
                            "unit": "Absolute",
                            "period": "TTM",
                            "source_name": "Public Financial Quote Summary",
                            "source_url": f"https://finance.yahoo.com/quote/{org.ticker}",
                            "status": STATUS_FOUND,
                            "is_calculated": False,
                            "notes": "Reported Trailing Twelve Months"
                        })
                    if "operatingCashflow" in fin and fin["operatingCashflow"].get("raw"):
                        raw_records.append({
                            "metric_name": "Operating Cash Flow",
                            "value": float(fin["operatingCashflow"]["raw"]),
                            "currency": "USD",
                            "unit": "Absolute",
                            "period": "TTM",
                            "source_name": "Public Financial Quote Summary",
                            "source_url": f"https://finance.yahoo.com/quote/{org.ticker}",
                            "status": STATUS_FOUND,
                            "is_calculated": False,
                            "notes": "Reported Trailing Twelve Months"
                        })
                    if "totalDebt" in fin and fin["totalDebt"].get("raw"):
                        raw_records.append({
                            "metric_name": "Borrowings (Debt)",
                            "value": float(fin["totalDebt"]["raw"]),
                            "currency": "USD",
                            "unit": "Absolute",
                            "period": "Most Recent Quarter",
                            "source_name": "Public Financial Quote Summary",
                            "source_url": f"https://finance.yahoo.com/quote/{org.ticker}",
                            "status": STATUS_FOUND,
                            "is_calculated": False,
                            "notes": "Reported Total Debt"
                        })
                    if "totalCash" in fin and fin["totalCash"].get("raw"):
                        raw_records.append({
                            "metric_name": "Cash and Cash Equivalents",
                            "value": float(fin["totalCash"]["raw"]),
                            "currency": "USD",
                            "unit": "Absolute",
                            "period": "Most Recent Quarter",
                            "source_name": "Public Financial Quote Summary",
                            "source_url": f"https://finance.yahoo.com/quote/{org.ticker}",
                            "status": STATUS_FOUND,
                            "is_calculated": False,
                            "notes": "Reported Total Cash & Equivalents"
                        })
            except Exception as e:
                logger.warning(f"Supplementary public quote check error: {e}")

        # 5. Deduplicate and clean records
        validated_records = DataValidator.deduplicate_and_clean(raw_records)

        # 6. Map all standard metrics to ensure three distinct availability statuses:
        # - PUBLIC INFORMATION FOUND
        # - NOT PUBLICLY AVAILABLE
        # - INFORMATION IS PRIVATE / ACCESS RESTRICTED
        found_metrics = {r["metric_name"]: r for r in validated_records}
        final_records = []

        for metric in self.STANDARD_METRICS:
            if metric in found_metrics:
                final_records.append(found_metrics[metric])
            else:
                # Distinguish if private/restricted or simply not publicly available
                is_restricted = False
                # If organization is strictly non-listed and private, balance sheet details might be private
                if not org.is_listed and metric in ["Operating Cash Flow", "Borrowings (Debt)", "Capital Expenditure"]:
                    status = STATUS_RESTRICTED
                    notes = "Metric is confidential / private or restricted to regulatory filings."
                else:
                    status = STATUS_NOT_AVAILABLE
                    notes = "Metric not found in accessible public web reports or SEC filings."

                final_records.append({
                    "metric_name": metric,
                    "value": None,
                    "currency": "USD",
                    "unit": "Absolute",
                    "period": "N/A",
                    "source_name": "Public Search Index",
                    "source_url": None,
                    "status": status,
                    "is_calculated": False,
                    "notes": notes
                })

        # 7. Persist to SQLite Database
        self._save_to_database(org.id, final_records)

        return final_records

    def _save_to_database(self, org_id: int, records: List[Dict[str, Any]]):
        """Saves or updates financial data rows in DB."""
        session = SessionLocal()
        try:
            # Clear old records for this org to prevent duplication
            session.query(FinancialData).filter(FinancialData.org_id == org_id).delete()
            for r in records:
                db_item = FinancialData(
                    org_id=org_id,
                    metric_name=r.get("metric_name"),
                    value=r.get("value"),
                    currency=r.get("currency", "USD"),
                    unit=r.get("unit", "Absolute"),
                    period=r.get("period", "N/A"),
                    source_name=r.get("source_name"),
                    source_url=r.get("source_url"),
                    status=r.get("status"),
                    is_calculated=r.get("is_calculated", False),
                    publication_date=r.get("publication_date"),
                    notes=r.get("notes")
                )
                session.add(db_item)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving financial records to DB: {e}")
        finally:
            session.close()

    def get_saved_financials(self, org_id: int) -> List[Dict[str, Any]]:
        """Retrieves saved financial records from DB."""
        session = SessionLocal()
        try:
            records = session.query(FinancialData).filter(FinancialData.org_id == org_id).all()
            return [
                {
                    "metric_name": r.metric_name,
                    "value": r.value,
                    "currency": r.currency,
                    "unit": r.unit,
                    "period": r.period,
                    "source_name": r.source_name,
                    "source_url": r.source_url,
                    "status": r.status,
                    "is_calculated": r.is_calculated,
                    "publication_date": r.publication_date,
                    "notes": r.notes
                }
                for r in records
            ]
        finally:
            session.close()
