"""
Financial mathematics and ratio calculation utilities.
Provides exact formulas for profitability, liquidity, investment returns,
and currency formatting with Indian number system support.
"""

from typing import List, Optional, Union
import numpy as np


def calculate_operating_profit(revenue: float, operating_expenses: float) -> float:
    """Operating Profit = Revenue - Operating Expenses"""
    return round(float(revenue) - float(operating_expenses), 2)


def calculate_net_profit(operating_profit: float, taxes: float = 0.0, loan_payments: float = 0.0) -> float:
    """Net Profit = Operating Profit - Taxes - Loan Payments"""
    return round(float(operating_profit) - float(taxes) - float(loan_payments), 2)


def calculate_profit_margin(net_profit: float, revenue: float) -> float:
    """Profit Margin (%) = (Net Profit / Revenue) * 100"""
    if revenue == 0:
        return 0.0
    return round((float(net_profit) / float(revenue)) * 100.0, 2)


def calculate_current_ratio(assets: float, liabilities: float) -> float:
    """Current / Liquidity Ratio = Total Assets / Total Liabilities"""
    if liabilities <= 0:
        return 99.99 if assets > 0 else 0.0
    return round(float(assets) / float(liabilities), 2)


def calculate_debt_ratio(liabilities: float, assets: float) -> float:
    """Debt Ratio = Total Liabilities / Total Assets"""
    if assets <= 0:
        return 1.0 if liabilities > 0 else 0.0
    return round(float(liabilities) / float(assets), 4)


def calculate_roi(gain: float, cost: float) -> float:
    """Return on Investment (%) = ((Gain - Cost) / Cost) * 100"""
    if cost <= 0:
        return 0.0
    return round(((float(gain) - float(cost)) / float(cost)) * 100.0, 2)


def calculate_simple_interest(principal: float, annual_rate: float, time_years: float) -> float:
    """Simple Interest = P * r * t"""
    return round(float(principal) * float(annual_rate) * float(time_years), 2)


def calculate_compound_interest(
    principal: float, annual_rate: float, time_years: float, compounding_frequency: int = 1
) -> float:
    """
    Compound Amount = P * (1 + r/n)^(n*t)
    Returns total interest earned: Compound Amount - Principal
    """
    if principal <= 0 or compounding_frequency <= 0:
        return 0.0
    total_amount = float(principal) * ((1 + (float(annual_rate) / compounding_frequency)) ** (compounding_frequency * float(time_years)))
    return round(total_amount - float(principal), 2)


def calculate_npv(discount_rate: float, initial_investment: float, cash_flows: List[float]) -> float:
    """
    Net Present Value (NPV) = sum_{t=1}^n [ CF_t / (1 + r)^t ] - Initial Investment
    """
    if not cash_flows:
        return round(-float(initial_investment), 2)
    pv_flows = sum(cf / ((1.0 + float(discount_rate)) ** (t + 1)) for t, cf in enumerate(cash_flows))
    return round(float(pv_flows) - float(initial_investment), 2)


def format_currency(amount: Union[int, float], currency_symbol: str = "₹", abbreviate: bool = False) -> str:
    """
    Formats amounts in clean Indian financial formatting (Crores / Lakhs)
    or standard commas.
    Examples:
    10000000 -> ₹1.00 Cr (abbreviate=True) or ₹1,00,00,000.00
    100000   -> ₹1.00 Lakh (abbreviate=True) or ₹1,00,000.00
    """
    if amount is None or (isinstance(amount, float) and np.isnan(amount)):
        return f"{currency_symbol}0.00"

    val = float(amount)
    is_negative = val < 0
    val_abs = abs(val)

    prefix = f"-{currency_symbol}" if is_negative else currency_symbol

    if abbreviate:
        if val_abs >= 10_000_000:  # 1 Crore
            return f"{prefix}{val_abs / 10_000_000:.2f} Cr"
        elif val_abs >= 100_000:   # 1 Lakh
            return f"{prefix}{val_abs / 100_000:.2f} L"
        elif val_abs >= 1_000:
            return f"{prefix}{val_abs / 1_000:.1f} K"
        else:
            return f"{prefix}{val_abs:.2f}"

    # Indian numbering format grouping: last 3 digits, then groups of 2 digits
    parts = f"{val_abs:.2f}".split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) <= 3:
        formatted_int = integer_part
    else:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        formatted_int = ",".join(groups) + "," + last_three

    return f"{prefix}{formatted_int}.{decimal_part}"
