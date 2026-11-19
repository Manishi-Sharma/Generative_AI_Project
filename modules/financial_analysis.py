"""
Financial analysis and ratio evaluation module.
Computes DuPont decomposition, solvency health scores, and trend metrics.
"""

from typing import Dict, Any, List
import pandas as pd
from utils.calculations import (
    calculate_operating_profit,
    calculate_net_profit,
    calculate_profit_margin,
    calculate_current_ratio,
    calculate_debt_ratio,
    calculate_roi,
)


def compute_financial_health_score(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes an integrated 0-100 financial health index based on:
    - Profitability (30%)
    - Liquidity / Solvency (30%)
    - Cash cushion / Reserves (20%)
    - Operating Efficiency (20%)
    """
    margin = summary.get("profit_margin", 0.0)
    curr_ratio = summary.get("current_ratio", 1.0)
    debt_ratio = summary.get("debt_ratio", 0.5)
    cash = summary.get("cash_reserves", 0.0)
    opex = summary.get("total_expenses", 1.0)

    # 1. Profit score (0 to 30)
    if margin >= 20.0:
        profit_score = 30.0
    elif margin >= 10.0:
        profit_score = 22.0
    elif margin >= 0.0:
        profit_score = 15.0
    else:
        profit_score = max(0.0, 10.0 + margin)

    # 2. Liquidity score (0 to 30)
    if curr_ratio >= 2.0:
        liq_score = 30.0
    elif curr_ratio >= 1.2:
        liq_score = 22.0
    elif curr_ratio >= 1.0:
        liq_score = 15.0
    else:
        liq_score = max(0.0, curr_ratio * 12.0)

    # 3. Solvency & Debt score (0 to 20)
    if debt_ratio <= 0.3:
        solv_score = 20.0
    elif debt_ratio <= 0.6:
        solv_score = 14.0
    elif debt_ratio <= 0.8:
        solv_score = 8.0
    else:
        solv_score = 3.0

    # 4. Cash reserve buffer score (0 to 20)
    monthly_burn = (opex / 12.0) if opex > 0 else 1.0
    months_buffer = cash / monthly_burn if monthly_burn > 0 else 0.0
    if months_buffer >= 6.0:
        cash_score = 20.0
    elif months_buffer >= 3.0:
        cash_score = 14.0
    elif months_buffer >= 1.0:
        cash_score = 8.0
    else:
        cash_score = 2.0

    total_score = round(profit_score + liq_score + solv_score + cash_score, 1)

    if total_score >= 80:
        grade = "A (Exceptional Resilience)"
        color = "#10b981"
    elif total_score >= 65:
        grade = "B (Sound Financial Health)"
        color = "#3b82f6"
    elif total_score >= 50:
        grade = "C (Adequate - Watch Working Capital)"
        color = "#f59e0b"
    else:
        grade = "D (Distressed - Corrective Action Required)"
        color = "#f43f5e"

    return {
        "score": total_score,
        "grade": grade,
        "color": color,
        "breakdown": {
            "Profitability": round(profit_score, 1),
            "Liquidity": round(liq_score, 1),
            "Solvency": round(solv_score, 1),
            "Cash Buffer": round(cash_score, 1),
        },
    }
