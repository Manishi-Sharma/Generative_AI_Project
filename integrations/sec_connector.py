import requests
import json
import logging
from typing import Dict, Any, List, Optional
from config import SEC_USER_AGENT

logger = logging.getLogger(__name__)

class SECConnector:
    """
    US SEC EDGAR Public Data Connector.
    Uses free public endpoints with required User-Agent headers compliant with SEC fair access policies.
    """
    BASE_URL = "https://data.sec.gov"
    TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self, user_agent: str = SEC_USER_AGENT):
        self.headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        self.www_headers = {
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self._ticker_map: Optional[Dict[str, Any]] = None

    def _get_ticker_map(self) -> Dict[str, Any]:
        """Loads and caches SEC ticker to CIK mapping."""
        if self._ticker_map is not None:
            return self._ticker_map

        try:
            resp = requests.get(self.TICKERS_URL, headers=self.www_headers, timeout=10)
            if resp.status_code == 200:
                self._ticker_map = resp.json()
                return self._ticker_map
        except Exception as e:
            logger.warning(f"Error fetching SEC company tickers: {e}")

        self._ticker_map = {}
        return self._ticker_map

    def find_company(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches SEC company index for matches by name or ticker.
        """
        query_norm = query.strip().lower()
        mapping = self._get_ticker_map()
        results = []

        for _, item in mapping.items():
            title = str(item.get("title", "")).lower()
            ticker = str(item.get("ticker", "")).lower()
            cik = str(item.get("cik_str", ""))

            # Direct match or substring match
            if query_norm == ticker or query_norm in title or query_norm in ticker:
                results.append({
                    "name": item.get("title"),
                    "ticker": item.get("ticker"),
                    "cik": cik.zfill(10),
                    "source": "U.S. SEC EDGAR Database",
                    "stock_exchange": "US (SEC Registered)",
                    "country": "United States / FPI"
                })
                if len(results) >= 5:
                    break

        return results

    def get_company_facts(self, cik: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves company facts / XBRL disclosures from SEC EDGAR.
        """
        cik_clean = str(cik).strip().zfill(10)
        url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik_clean}.json"

        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(f"SEC API returned status {resp.status_code} for CIK {cik_clean}")
                return None
        except Exception as e:
            logger.error(f"Error querying SEC company facts for CIK {cik_clean}: {e}")
            return None

    def extract_standard_financials(self, facts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts key standardized metrics from SEC XBRL taxonomy (us-gaap or dei).
        """
        if not facts_data or "facts" not in facts_data:
            return []

        entity_name = facts_data.get("entityName", "SEC Registered Entity")
        facts = facts_data.get("facts", {})
        us_gaap = facts.get("us-gaap", {})

        # Key taxonomy concepts to look for
        concept_map = {
            "Revenues": "Revenue",
            "RevenueFromContractWithCustomerExcludingAssessedTax": "Revenue",
            "SalesRevenueNet": "Revenue",
            "OperatingExpenses": "Operating Expenses",
            "CostsAndExpenses": "Operating Expenses",
            "OperatingIncomeLoss": "Operating Profit",
            "NetIncomeLoss": "Net Profit",
            "Assets": "Total Assets",
            "Liabilities": "Total Liabilities",
            "StockholdersEquity": "Shareholders' Equity",
            "CashAndCashEquivalentsAtCarryingValue": "Cash and Cash Equivalents",
            "LongTermDebtNoncurrent": "Borrowings (Long-term)",
            "NetCashProvidedByUsedInOperatingActivities": "Operating Cash Flow",
            "PaymentsToAcquirePropertyPlantAndEquipment": "Capital Expenditure",
            "ResearchAndDevelopmentExpense": "Research & Development"
        }

        extracted = []

        for concept, display_name in concept_map.items():
            if concept in us_gaap:
                units_dict = us_gaap[concept].get("units", {})
                # USD or principal currency
                unit_key = "USD" if "USD" in units_dict else (list(units_dict.keys())[0] if units_dict else None)
                if not unit_key:
                    continue

                items = units_dict[unit_key]
                # Filter for annual filings (10-K) or quarterly (10-Q) with form specified
                annual_items = [i for i in items if i.get("form") in ["10-K", "20-F", "10-Q"]]
                if not annual_items:
                    annual_items = items

                # Sort by end date descending
                annual_items.sort(key=lambda x: str(x.get("end", "")), reverse=True)

                if annual_items:
                    latest = annual_items[0]
                    # Also collect previous if available
                    val = latest.get("val")
                    period = latest.get("fy", "")
                    end_date = latest.get("end", "")
                    form = latest.get("form", "10-K")
                    acc_num = latest.get("accn", "")

                    sec_doc_url = f"https://www.sec.gov/edgar/browse/?CIK={facts_data.get('cik')}"
                    if acc_num:
                        clean_acc = acc_num.replace("-", "")
                        sec_doc_url = f"https://www.sec.gov/Archives/edgar/data/{facts_data.get('cik')}/{clean_acc}/{acc_num}-index.htm"

                    period_label = f"FY{period}" if period else f"Period ending {end_date}"
                    extracted.append({
                        "metric_name": display_name,
                        "value": float(val) if val is not None else None,
                        "currency": unit_key,
                        "unit": "Absolute",
                        "period": f"{period_label} ({form})",
                        "source_name": f"U.S. SEC EDGAR ({form} Filing)",
                        "source_url": sec_doc_url,
                        "publication_date": end_date,
                        "status": "PUBLIC INFORMATION FOUND",
                        "is_calculated": False,
                        "notes": f"Disclosed under US-GAAP {concept}"
                    })

        return extracted
