"""
Page: Scenario Comparison
Compares alternative strategic trajectories side-by-side,
evaluating baseline, optimistic, pessimistic, and custom policy scenarios.
"""

from typing import Any
import json
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from database.models import Scenario
from modules.butterfly_engine import ButterflyEngine
from modules.financial_data import get_latest_financial_summary
from utils.calculations import format_currency
from utils.visualisations import plot_scenario_comparison


def render_scenarios_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## ⚖️ Strategic Scenario Comparison")
    st.markdown(f"**Entity:** `{current_org.name}` | Comparative Horizon Analysis")

    with get_db_context() as db:
        summary = get_latest_financial_summary(db, current_org.id)
        saved_scenarios = db.query(Scenario).filter(Scenario.org_id == current_org.id).all()

    currency = current_org.currency
    base_financials = {
        "revenue": summary["total_revenue"] or 30_000_000.0,
        "operating_expenses": summary["total_expenses"] or 22_000_000.0,
        "cash_reserves": summary["cash_reserves"] or 15_000_000.0,
        "assets": 120_000_000.0,
        "liabilities": 35_000_000.0,
    }

    engine = ButterflyEngine()

    tab_macro, tab_custom = st.tabs([
        "🌐 Macroeconomic Scenarios (Baseline / Bull / Bear)",
        "📁 Saved Organisational Scenarios"
    ])

    with tab_macro:
        st.markdown("### Standard Macro Stress-Test Comparison")
        st.write("Examines how a baseline operational policy performs across three divergent macroeconomic regimes over a 5-year horizon.")

        # Baseline shocks (e.g. 2% opex cut, 5% R&D increase)
        default_shocks = {"Operating Expenses": -0.02, "Research and Development": 0.05}
        macro_results = engine.simulate_scenarios(default_shocks, base_financials)

        # Plot comparison chart
        st.plotly_chart(plot_scenario_comparison(macro_results), use_container_width=True)

        # Numerical comparison table
        table_rows = []
        for sc_name, sc_vals in macro_results.items():
            table_rows.append({
                "Scenario": sc_name,
                "Projected Revenue": format_currency(sc_vals["Revenue"], currency),
                "Operating Expenses": format_currency(sc_vals["Operating Expenses"], currency),
                "Net Profit": format_currency(sc_vals["Net Profit"], currency),
                "Cash Reserves": format_currency(sc_vals["Cash Reserves"], currency),
                "Liquidity Ratio": f"{sc_vals['Liquidity Ratio']:.2f}x",
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

    with tab_custom:
        st.markdown("### User-Defined Organisational Scenarios")
        if not saved_scenarios:
            st.info("No custom scenarios saved yet. Use the Butterfly Effect Simulator to configure and save strategic scenarios.")
        else:
            custom_results = {}
            for sc in saved_scenarios:
                try:
                    params = json.loads(sc.parameter_changes_json)
                except Exception:
                    params = {}

                sim = engine.calculate_ripple(initial_shocks=params, max_periods=5)
                deltas = sim["final_5yr_deltas"]

                proj_rev = base_financials["revenue"] * (1.0 + deltas.get("Revenue", 0.0))
                proj_exp = base_financials["operating_expenses"] * (1.0 + deltas.get("Operating Expenses", 0.0))
                proj_profit = proj_rev - proj_exp
                proj_cash = base_financials["cash_reserves"] * (1.0 + deltas.get("Cash Reserves", 0.0))

                custom_results[sc.name] = {
                    "Revenue": round(proj_rev, 2),
                    "Operating Expenses": round(proj_exp, 2),
                    "Net Profit": round(proj_profit, 2),
                    "Cash Reserves": round(proj_cash, 2),
                    "Liquidity Ratio": 2.2,
                }

            st.plotly_chart(plot_scenario_comparison(custom_results), use_container_width=True)

            custom_rows = []
            for sc in saved_scenarios:
                vals = custom_results.get(sc.name, {})
                custom_rows.append({
                    "Scenario Name": sc.name,
                    "Type": sc.scenario_type,
                    "Projected Revenue": format_currency(vals.get("Revenue", 0), currency),
                    "Net Profit": format_currency(vals.get("Net Profit", 0), currency),
                    "Cash Reserves": format_currency(vals.get("Cash Reserves", 0), currency),
                    "Description": sc.description or "None",
                })
            st.dataframe(pd.DataFrame(custom_rows), use_container_width=True)
