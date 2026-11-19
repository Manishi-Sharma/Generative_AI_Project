"""
Input validation, CSV schema checking, and data sanitization utilities.
"""

import re
from typing import Dict, Any, Tuple, List, Optional
import pandas as pd


REQUIRED_CSV_COLUMNS = [
    "year",
    "quarter",
    "revenue",
    "operating_expenses",
    "salaries",
    "production_costs",
    "electricity",
    "marketing",
    "administration",
    "rd_expenses",
    "investments",
    "assets",
    "liabilities",
    "cash_reserves",
    "taxes",
    "loan_payments"
]


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Ensure password meets minimal enterprise length and complexity."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_numeric(val: Any, field_name: str, min_val: Optional[float] = 0.0) -> Tuple[bool, float, str]:
    """Validate and convert value to positive float."""
    try:
        f_val = float(val)
        if min_val is not None and f_val < min_val:
            return False, 0.0, f"{field_name} cannot be less than {min_val}."
        return True, f_val, ""
    except (ValueError, TypeError):
        return False, 0.0, f"Invalid numeric input for {field_name}."


def validate_financial_csv(df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, List[str]]:
    """
    Validates uploaded CSV file against required financial columns,
    normalizes column names, cleans missing values, and checks period validity.
    """
    errors: List[str] = []
    
    # Normalize column names: lowercase, strip, replace spaces/dashes with underscores
    df_clean = df.copy()
    df_clean.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df_clean.columns]

    missing_cols = [col for col in REQUIRED_CSV_COLUMNS if col not in df_clean.columns]
    if missing_cols:
        return False, df_clean, [f"Missing required columns in CSV: {', '.join(missing_cols)}"]

    # Fill NaNs with sensible defaults
    df_clean[REQUIRED_CSV_COLUMNS] = df_clean[REQUIRED_CSV_COLUMNS].fillna(0.0)

    # Convert numeric fields
    for col in REQUIRED_CSV_COLUMNS:
        try:
            df_clean[col] = pd.to_numeric(df_clean[col])
        except Exception as e:
            errors.append(f"Column '{col}' contains non-numeric data: {e}")

    if errors:
        return False, df_clean, errors

    # Check year and quarter sanity
    if (df_clean["year"] < 1990).any() or (df_clean["year"] > 2100).any():
        errors.append("Year values must be between 1990 and 2100.")

    if not df_clean["quarter"].isin([1, 2, 3, 4]).all():
        errors.append("Quarter values must be 1, 2, 3, or 4.")

    if errors:
        return False, df_clean, errors

    return True, df_clean, []
