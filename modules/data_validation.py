import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates, deduplicates, and checks sanity of retrieved financial records.
    """
    REQUIRED_METRICS = [
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
        "Capital Expenditure"
    ]

    @staticmethod
    def deduplicate_and_clean(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Keeps highest fidelity record per metric name (preferring SEC EDGAR / Official Filings).
        """
        metric_map = {}

        # Sort priority: SEC EDGAR > Official Filings > PDF > Web Tables > Web Page Content
        priority_weights = {
            "sec edgar": 100,
            "annual": 80,
            "quarterly": 70,
            "disclosure table": 50,
            "web page": 20
        }

        for rec in records:
            metric = rec.get("metric_name")
            if not metric:
                continue

            src = str(rec.get("source_name", "")).lower()
            score = 10
            for k, w in priority_weights.items():
                if k in src:
                    score = max(score, w)

            val = rec.get("value")
            if val is None or val <= 0:
                continue

            if metric not in metric_map or score > metric_map[metric]["score"]:
                metric_map[metric] = {
                    "record": rec,
                    "score": score
                }

        cleaned = [item["record"] for item in metric_map.values()]
        return cleaned

    @staticmethod
    def audit_sanity(metrics_dict: Dict[str, float]) -> List[str]:
        """
        Runs accounting integrity and sanity checks across available numbers.
        Returns list of warnings or findings.
        """
        warnings = []
        rev = metrics_dict.get("Revenue")
        net_profit = metrics_dict.get("Net Profit")
        op_profit = metrics_dict.get("Operating Profit")
        assets = metrics_dict.get("Total Assets")
        liab = metrics_dict.get("Total Liabilities")
        equity = metrics_dict.get("Shareholders' Equity")

        if rev is not None and net_profit is not None:
            if net_profit > rev:
                warnings.append("Note: Net Profit exceeds Revenue. Check for one-off extraordinary items or accounting reclassifications.")

        if op_profit is not None and rev is not None:
            if op_profit > rev:
                warnings.append("Note: Operating Profit reported higher than gross revenue; verifying classification.")

        if assets is not None and liab is not None and equity is not None:
            diff = abs(assets - (liab + equity))
            if assets > 0 and (diff / assets) > 0.15:
                warnings.append(f"Balance Sheet discrepancy: Assets ({assets:,.0f}) does not match Liabilities + Equity ({(liab + equity):,.0f}) within 15%.")

        return warnings
