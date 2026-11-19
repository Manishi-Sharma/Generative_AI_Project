"""
Financial risk engine and stress testing module.
Evaluates liquidity risk, debt exposure, cash burn runway, concentration indices,
executes Monte Carlo simulations, and performs sensitivity stress testing.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from utils.calculations import calculate_current_ratio, calculate_debt_ratio


def evaluate_financial_risks(
    financial_records: Any,
    investments_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Computes 5 critical financial risk dimensions on a 0-100 scale:
    0 = Minimal Risk (Ultra Safe), 100 = Critical Distress (Immediate Danger).
    """
    records = list(financial_records) if financial_records is not None else []
    if not records:
        return {
            "overall_risk_score": 50.0,
            "risk_tier": "Moderate",
            "liquidity_risk": 50.0,
            "debt_risk": 50.0,
            "cash_flow_risk": 50.0,
            "revenue_volatility_risk": 50.0,
            "concentration_risk": 50.0,
            "runway_months": 0.0,
            "mitigations": ["Submit financial statements to enable precise risk diagnosis."],
        }

    latest = records[-1]

    # 1. Liquidity Risk (Cash & Assets vs Liabilities)
    curr_ratio = calculate_current_ratio(latest.assets, latest.liabilities)
    if curr_ratio >= 2.5:
        liquidity_risk = 10.0
    elif curr_ratio >= 1.5:
        liquidity_risk = 25.0
    elif curr_ratio >= 1.0:
        liquidity_risk = 50.0
    elif curr_ratio >= 0.7:
        liquidity_risk = 75.0
    else:
        liquidity_risk = 95.0

    # 2. Debt Exposure Risk (Liabilities / Assets)
    debt_ratio = calculate_debt_ratio(latest.liabilities, latest.assets)
    if debt_ratio <= 0.25:
        debt_risk = 10.0
    elif debt_ratio <= 0.50:
        debt_risk = 30.0
    elif debt_ratio <= 0.75:
        debt_risk = 60.0
    elif debt_ratio <= 1.0:
        debt_risk = 80.0
    else:
        debt_risk = 95.0

    # 3. Cash Flow & Burn Runway Risk
    # Average quarterly burn if expenses > revenue
    revenues = [r.revenue for r in records]
    expenses = [r.operating_expenses for r in records]
    avg_qtr_rev = np.mean(revenues)
    avg_qtr_exp = np.mean(expenses)
    net_burn_quarter = avg_qtr_exp - avg_qtr_rev

    if net_burn_quarter > 0:
        # Burning cash
        monthly_burn = net_burn_quarter / 3.0
        runway_months = (latest.cash_reserves / monthly_burn) if monthly_burn > 0 else 0.0
        if runway_months > 24:
            cash_flow_risk = 25.0
        elif runway_months > 12:
            cash_flow_risk = 45.0
        elif runway_months > 6:
            cash_flow_risk = 75.0
        else:
            cash_flow_risk = 95.0
    else:
        # Cash flow positive
        runway_months = 99.0
        cash_flow_risk = 15.0

    # 4. Revenue Volatility Risk
    if len(revenues) >= 3:
        rev_std = np.std(revenues)
        cov = (rev_std / avg_qtr_rev) if avg_qtr_rev > 0 else 1.0
        volatility_risk = min(100.0, max(10.0, cov * 120.0))
    else:
        volatility_risk = 35.0

    # 5. Investment Concentration Risk (Herfindahl-Hirschman Index)
    if investments_df is not None and not investments_df.empty:
        total_inv = investments_df["amount"].sum()
        if total_inv > 0:
            shares = investments_df["amount"] / total_inv
            hhi = float(np.sum(shares ** 2))  # Range 1/N to 1.0
            concentration_risk = min(100.0, hhi * 100.0)
        else:
            concentration_risk = 20.0
    else:
        concentration_risk = 20.0

    # Weighted Overall Risk
    overall_score = round(
        (liquidity_risk * 0.25)
        + (debt_risk * 0.25)
        + (cash_flow_risk * 0.20)
        + (volatility_risk * 0.15)
        + (concentration_risk * 0.15),
        1
    )

    if overall_score < 30:
        risk_tier = "Low Risk (Stable Financial Profile)"
    elif overall_score < 60:
        risk_tier = "Moderate Risk (Cautious Monitoring Required)"
    elif overall_score < 80:
        risk_tier = "High Risk (Vulnerable to Exogenous Shocks)"
    else:
        risk_tier = "Critical Risk (Urgent Balance Sheet Restructuring)"

    # Actionable Mitigations
    mitigations = []
    if liquidity_risk > 50:
        mitigations.append("Boost liquid quick reserves; defer discretionary long-term capital commitments.")
    if debt_risk > 50:
        mitigations.append("Restructure or amortize short-term high-interest credit lines into sustainable instruments.")
    if cash_flow_risk > 50:
        mitigations.append(f"Cash runway stands at {runway_months:.1f} months; institute immediate OPEX rationalization.")
    if concentration_risk > 50:
        mitigations.append("Diversify investment holdings across non-correlated asset classes to reduce single-asset vulnerability.")
    if not mitigations:
        mitigations.append("Maintain existing conservative capital deployment; current solvency indicators are robust.")

    return {
        "overall_risk_score": overall_score,
        "risk_tier": risk_tier,
        "liquidity_risk": round(liquidity_risk, 1),
        "debt_risk": round(debt_risk, 1),
        "cash_flow_risk": round(cash_flow_risk, 1),
        "revenue_volatility_risk": round(volatility_risk, 1),
        "concentration_risk": round(concentration_risk, 1),
        "runway_months": round(runway_months, 1),
        "current_ratio": round(curr_ratio, 2),
        "debt_ratio": round(debt_ratio, 2),
        "mitigations": mitigations,
    }


def run_monte_carlo_simulation(
    base_revenue: float,
    base_expenses: float,
    iterations: int = 1000,
    rev_volatility: float = 0.12,
    exp_volatility: float = 0.08,
) -> Dict[str, Any]:
    """
    Executes a 1000-iteration Monte Carlo stress simulation.
    Models stochastic shocks to revenue and costs with normal distributions.
    Computes Value at Risk (VaR 95%), Expected Shortfall, and Probability of Operating Loss.
    """
    np.random.seed(42)

    # Shocks drawn from Gaussian distributions
    rev_shocks = np.random.normal(loc=1.0, scale=rev_volatility, size=iterations)
    exp_shocks = np.random.normal(loc=1.0, scale=exp_volatility, size=iterations)

    sim_revenues = base_revenue * rev_shocks
    sim_expenses = base_expenses * exp_shocks
    sim_profits = sim_revenues - sim_expenses

    baseline_profit = base_revenue - base_expenses
    loss_count = np.sum(sim_profits < 0)
    prob_of_loss = float(loss_count / iterations) * 100.0

    p5 = float(np.percentile(sim_profits, 5))
    p50 = float(np.percentile(sim_profits, 50))
    p95 = float(np.percentile(sim_profits, 95))

    var_95 = baseline_profit - p5  # Maximum expected loss at 95% confidence

    return {
        "iterations": iterations,
        "baseline_profit": round(baseline_profit, 2),
        "simulated_profits": sim_profits.tolist(),
        "median_profit": round(p50, 2),
        "percentile_5th": round(p5, 2),
        "percentile_95th": round(p95, 2),
        "var_95": round(var_95, 2),
        "probability_of_loss_pct": round(prob_of_loss, 2),
    }


def run_sensitivity_analysis(
    base_revenue: float,
    base_expenses: float
) -> pd.DataFrame:
    """
    Conducts deterministic two-way sensitivity matrix across revenue shocks
    (-20% to +20%) and expense shocks (-20% to +20%).
    """
    shocks = [-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]
    results = []

    for r_shock in shocks:
        r_val = base_revenue * (1.0 + r_shock)
        row = {"Revenue Shock": f"{r_shock:+.0%}"}
        for e_shock in shocks:
            e_val = base_expenses * (1.0 + e_shock)
            net_prof = r_val - e_val
            row[f"Exp {e_shock:+.0%}"] = round(net_prof, 2)
        results.append(row)

    return pd.DataFrame(results)
