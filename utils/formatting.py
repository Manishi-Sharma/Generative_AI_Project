from typing import Optional, Union

def format_currency(value: Optional[Union[float, int]], currency: str = "USD", unit: str = "Absolute") -> str:
    """Formats numeric value as a clean financial string with unit and currency."""
    if value is None:
        return "N/A"

    curr_symbol = {
        "USD": "$",
        "INR": "₹",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }.get(currency.upper(), f"{currency} ")

    abs_val = abs(value)
    sign = "-" if value < 0 else ""

    if unit.lower() in ["billions", "billion", "b"]:
        return f"{sign}{curr_symbol}{abs_val:,.2f} B"
    elif unit.lower() in ["millions", "million", "m"]:
        return f"{sign}{curr_symbol}{abs_val:,.2f} M"
    elif unit.lower() in ["crores", "crore", "cr"]:
        return f"{sign}{curr_symbol}{abs_val:,.2f} Cr"

    # Auto-scale large absolute numbers
    if abs_val >= 1e12:
        return f"{sign}{curr_symbol}{abs_val / 1e12:,.2f} Trillion"
    elif abs_val >= 1e9:
        return f"{sign}{curr_symbol}{abs_val / 1e9:,.2f} Billion"
    elif abs_val >= 1e6:
        return f"{sign}{curr_symbol}{abs_val / 1e6:,.2f} Million"
    elif abs_val >= 1e3:
        return f"{sign}{curr_symbol}{abs_val:,.2f}"
    else:
        return f"{sign}{curr_symbol}{abs_val:,.2f}"

def format_percentage(value: Optional[Union[float, int]], include_sign: bool = False) -> str:
    """Formats float as percentage string."""
    if value is None:
        return "N/A"
    if include_sign and value > 0:
        return f"+{value:.2f}%"
    return f"{value:.2f}%"

def clean_company_name(name: str) -> str:
    """Cleans up raw input company names."""
    return " ".join(name.strip().split())
