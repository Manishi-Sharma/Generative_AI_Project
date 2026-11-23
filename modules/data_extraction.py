import re
import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from utils.validators import sanitize_number

logger = logging.getLogger(__name__)

class DataExtractor:
    """
    Extracts structured financial disclosures from HTML pages and PDF reports.
    """
    METRIC_PATTERNS = {
        "Revenue": [
            r"(?:total\s+)?revenue[s]?\b",
            r"turnover\b",
            r"net\s+sales\b",
            r"income\s+from\s+operations\b"
        ],
        "Operating Expenses": [
            r"operating\s+expense[s]?\b",
            r"total\s+expenses\b",
            r"costs\s+and\s+expenses\b"
        ],
        "Operating Profit": [
            r"operating\s+(?:profit|income|loss)\b",
            r"ebit\b",
            r"operating\s+margin\b"
        ],
        "Net Profit": [
            r"net\s+(?:profit|income|loss)\b",
            r"profit\s+after\s+tax\b",
            r"pat\b",
            r"net\s+earnings\b"
        ],
        "Total Assets": [
            r"total\s+assets\b",
            r"total\s+current\s+and\s+non-current\s+assets\b"
        ],
        "Total Liabilities": [
            r"total\s+liabilities\b"
        ],
        "Shareholders' Equity": [
            r"(?:total\s+)?shareholders['’]?\s+equity\b",
            r"stockholders['’]?\s+equity\b",
            r"total\s+equity\b"
        ],
        "Cash and Cash Equivalents": [
            r"cash\s+and\s+cash\s+equivalents\b",
            r"cash\s+reserves\b",
            r"total\s+cash\b"
        ],
        "Borrowings (Debt)": [
            r"total\s+debt\b",
            r"borrowings\b",
            r"long-term\s+debt\b",
            r"total\s+borrowings\b"
        ],
        "Operating Cash Flow": [
            r"(?:net\s+)?cash\s+from\s+operating\s+activities\b",
            r"operating\s+cash\s+flow\b"
        ],
        "Capital Expenditure": [
            r"capital\s+expenditure[s]?\b",
            r"capex\b",
            r"additions\s+to\s+property[,\s]+plant\s+and\s+equipment\b"
        ],
        "Research & Development": [
            r"research\s+and\s+development\b",
            r"r&d\s+expenses?\b"
        ]
    }

    @staticmethod
    def extract_from_html(html_text: str, source_url: str = "") -> List[Dict[str, Any]]:
        """
        Parses HTML text and tables to discover financial metrics.
        """
        results = []
        soup = BeautifulSoup(html_text, "html.parser")

        # 1. Search in tabular data
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cols) >= 2:
                    label = cols[0]
                    val_str = cols[1]

                    for metric_name, patterns in DataExtractor.METRIC_PATTERNS.items():
                        for pat in patterns:
                            if re.search(pat, label, re.IGNORECASE):
                                val = sanitize_number(val_str)
                                if val is not None and val > 0:
                                    results.append({
                                        "metric_name": metric_name,
                                        "value": val,
                                        "currency": "USD" if "$" in val_str else ("INR" if "₹" in val_str else "Local"),
                                        "unit": "Absolute",
                                        "period": "Reported Period",
                                        "source_name": "Web Disclosure Table",
                                        "source_url": source_url,
                                        "status": "PUBLIC INFORMATION FOUND",
                                        "is_calculated": False,
                                        "notes": f"Extracted from row: {label}"
                                    })
                                break

        # 2. Search in raw paragraph/text snippets
        text = soup.get_text(separator=" ")
        extracted_from_text = DataExtractor.extract_from_text(text, source_url, "Web Page Content")
        results.extend(extracted_from_text)

        return results

    @staticmethod
    def extract_from_text(text: str, source_url: str = "", source_label: str = "Public Source") -> List[Dict[str, Any]]:
        """
        Regex scanner for sentences mentioning metric + currency/amount.
        """
        results = []
        # Pattern like: Revenue of $12.5 billion, Net profit was 3,400 Cr, etc.
        for metric_name, patterns in DataExtractor.METRIC_PATTERNS.items():
            for pat in patterns:
                # E.g. "Revenue was $15.2 billion" or "Net income: $4,500 million"
                regex = rf"(?:{pat})[^\d\n\.\$₹€£]{{0,30}}([\$₹€£]?\s*[\d,]+(?:\.\d+)?\s*(?:billion|million|cr|crore|trillion|b|m)?)"
                matches = re.finditer(regex, text, re.IGNORECASE)
                for m in matches:
                    val_str = m.group(1).strip()
                    val = sanitize_number(val_str)
                    if val is not None and val > 0:
                        currency = "USD" if "$" in val_str else ("INR" if "₹" in val_str or "cr" in val_str.lower() else "USD")
                        results.append({
                            "metric_name": metric_name,
                            "value": val,
                            "currency": currency,
                            "unit": "Absolute",
                            "period": "Latest Disclosed",
                            "source_name": source_label,
                            "source_url": source_url,
                            "status": "PUBLIC INFORMATION FOUND",
                            "is_calculated": False,
                            "notes": f"Matched snippet: '{m.group(0)[:60]}...'"
                        })
                        break # One per metric per pass
        return results

    @staticmethod
    def extract_from_pdf(pdf_path_or_bytes, source_url: str = "") -> List[Dict[str, Any]]:
        """
        Extracts text from PDF file using PyMuPDF (fitz) and scans for financial disclosures.
        """
        results = []
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf") if isinstance(pdf_path_or_bytes, (bytes, bytearray)) else fitz.open(pdf_path_or_bytes)
            full_text = []
            # Scan first 20 pages max to keep performant
            for page_idx in range(min(len(doc), 20)):
                page = doc[page_idx]
                full_text.append(page.get_text())
            doc.close()
            combined_text = "\n".join(full_text)
            results = DataExtractor.extract_from_text(combined_text, source_url, "Annual / Quarterly PDF Report")
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
        return results
