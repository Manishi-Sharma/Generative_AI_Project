"""
Tests for financial risk assessment, Monte Carlo simulations, and sensitivity analysis.
"""

from database.connection import get_db_context
from database.models import Organisation
from modules.financial_data import get_financial_records
from modules.risk_analysis import (
    evaluate_financial_risks,
    run_monte_carlo_simulation,
    run_sensitivity_analysis,
)


def test_evaluate_financial_risks():
    with get_db_context() as db:
        org = db.query(Organisation).first()
        records = get_financial_records(db, org.id)
        
        risks = evaluate_financial_risks(records)
        assert "overall_risk_score" in risks
        assert 0.0 <= risks["overall_risk_score"] <= 100.0
        assert "risk_tier" in risks
        assert "liquidity_risk" in risks
        assert "debt_risk" in risks
        assert "cash_flow_risk" in risks
        assert len(risks["mitigations"]) > 0


def test_monte_carlo_simulation():
    res = run_monte_carlo_simulation(
        base_revenue=10_000_000.0,
        base_expenses=8_000_000.0,
        iterations=1000,
    )
    assert res["iterations"] == 1000
    assert res["baseline_profit"] == 2_000_000.0
    assert len(res["simulated_profits"]) == 1000
    assert res["percentile_5th"] < res["median_profit"] < res["percentile_95th"]
    assert res["var_95"] > 0


def test_sensitivity_analysis():
    df_sens = run_sensitivity_analysis(
        base_revenue=10_000_000.0,
        base_expenses=8_000_000.0,
    )
    assert not df_sens.empty
    assert "Revenue Shock" in df_sens.columns
    # Check that +20% revenue with -20% expenses yields maximum profit
    max_prof = df_sens.loc[df_sens["Revenue Shock"] == "+20%", "Exp -20%"].values[0]
    # Revenue = 12M, Exp = 6.4M -> Profit = 5.6M
    assert max_prof == 5_600_000.0
