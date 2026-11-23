import re
from typing import Optional

def is_valid_url(url: Optional[str]) -> bool:
    if not url:
        return False
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def sanitize_number(val_str: str) -> Optional[float]:
    """Extracts numeric value from text like '$14,200.50 M' or '-15.4%'."""
    if not val_str:
        return None
    # Strip common non-numeric chars except digits, minus, period
    cleaned = val_str.replace(",", "").replace("$", "").replace("₹", "").replace("€", "").replace("£", "").strip()
    multiplier = 1.0
    upper = cleaned.upper()
    if upper.endswith("B") or "BILLION" in upper:
        multiplier = 1e9
        cleaned = re.sub(r'[A-Za-z]+', '', cleaned)
    elif upper.endswith("M") or "MILLION" in upper:
        multiplier = 1e6
        cleaned = re.sub(r'[A-Za-z]+', '', cleaned)
    elif upper.endswith("K") or "THOUSAND" in upper:
        multiplier = 1e3
        cleaned = re.sub(r'[A-Za-z]+', '', cleaned)
    elif upper.endswith("CR") or "CRORE" in upper:
        multiplier = 1e7
        cleaned = re.sub(r'[A-Za-z]+', '', cleaned)
    else:
        cleaned = re.sub(r'[A-Za-z%]+', '', cleaned)

    cleaned = cleaned.strip()
    try:
        return float(cleaned) * multiplier
    except ValueError:
        return None
