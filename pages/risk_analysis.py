"""
Page: Financial Risk Engine & Stress Testing
Evaluates multi-dimensional financial risk vectors, executes 1,000-iteration
Monte Carlo simulations, and generates two-way sensitivity matrices.
"""

from typing import Any
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from modules.financial_data import get_financial_dataframe
from modules.investment import get_investments_dataframe
from modules.risk_analysis import (
    evaluate_financial_risks,
    run_monte_carlo_simulation,
    run_sensitivity_analysis,
)
from utils.calculations import format_currency
from utils.visualisations import plot_risk_radar, plot_monte_carlo_distribution


def render_risk_analysis_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 🛡️ Enterprise Financial Risk & Stress Engine")
    st.markdown(f"**Entity:** `{current_org.name}` | Solvency & Quantitative Stress Testing")

    with get_db_context() as db:
        df_fin = get_financial_dataframe(db, current_org.id)
        df_inv = get_investments_dataframe(db, current_org.id)

    if df_fin.empty:
        st.warning("Insufficient financial data recorded to execute risk diagnosis.")
        return

    currency = current_org.currency
    records = list(df_fin.itertuples())
    risk_profile = evaluate_financial_risks(records, df_inv)

    # Risk Score Banner
    overall = risk_profile["overall_risk_score"]
    risk_color = "#10b981" if overall < 35 else "#f59e0b" if overall < 70 else "#f43f5e"

    st.markdown(f"""
    <div style="background-color: #1c2541; border: 1px solid #273549; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 13px; color: #94a3b8; text-transform: uppercase;">Overall Enterprise Risk Exposure</div>
                <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 6px;">
                    <span style="font-size: 42px; font-weight: 800; color: {risk_color};">{overall}</span>
                    <span style="font-size: 18px; color: #94a3b8;">/ 100</span>
                    <span style="font-size: 16px; font-weight: 600; color: {risk_color};">{risk_profile['risk_tier']}</span>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 12px; color: #94a3b8;">Cash Runway: <b>{risk_profile['runway_months']:.1f} Months</b></div>
                <div style="font-size: 12px; color: #94a3b8;">Current Ratio: <b>{risk_profile['current_ratio']:.2f}x</b></div>
                <div style="font-size: 12px; color: #94a3b8;">Debt Leverage: <b>{risk_profile['debt_ratio']:.2f}</b></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_radar, tab_mc, tab_sens = st.tabs([
        "🕸️ Risk Vector Radar & Mitigations",
        "🎲 Monte Carlo Stress Simulation",
        "⚡ Sensitivity & Shock Matrix"
    ])

    with tab_radar:
        col_r1, col_r2 = st.columns([1, 1.2])
        with col_r1:
            radar_dict = {
                "Liquidity Risk": risk_profile["liquidity_risk"],
                "Debt Risk": risk_profile["debt_risk"],
                "Cash Flow Burn": risk_profile["cash_flow_risk"],
                "Revenue Volatility": risk_profile["revenue_volatility_risk"],
                "Concentration Risk": risk_profile["concentration_risk"],
            }
            st.plotly_chart(plot_risk_radar(radar_dict), use_container_width=True)

        with col_r2:
            st.markdown("#### Strategic Mitigations & Board Directives")
            for m in risk_profile["mitigations"]:
                st.markdown(f"- 🛡️ {m}")

            st.markdown("---")
            st.markdown("#### Key Solvency Ratios")
            st.write(f"- **Liquidity Risk ({risk_profile['liquidity_risk']}/100):** Based on current asset coverage.")
            st.write(f"- **Debt Exposure ({risk_profile['debt_risk']}/100):** Total liabilities vs asset backing.")
            st.write(f"- **Burn Runway ({risk_profile['cash_flow_risk']}/100):** Operational cash burn resilience.")

    with tab_mc:
        st.markdown("### Stochastic Monte Carlo Simulation (1,000 Iterations)")
        st.write("Simulates 1,000 correlated revenue and cost volatility shocks to model probability of operating shortfall and Value at Risk (VaR).")

        base_rev = float(df_fin["revenue"].iloc[-1])
        base_exp = float(df_fin["operating_expenses"].iloc[-1])

        mc_res = run_monte_carlo_simulation(
            base_revenue=base_rev,
            base_expenses=base_exp,
            iterations=1000,
            rev_volatility=0.12,
            exp_volatility=0.08,
        )

        st.plotly_chart(
            plot_monte_carlo_distribution(
                mc_res["simulated_profits"],
                mc_res["baseline_profit"],
                metric_name="Quarterly Net Operating Profit"
            ),
            use_container_width=True,
        )

        mc_c1, mc_c2, mc_c3 = st.columns(3)
        with mc_c1:
            st.metric("5th Percentile Outcome (VaR 95%)", format_currency(mc_res["percentile_5th"], currency))
        with mc_c2:
            st.metric("Median Simulated Profit", format_currency(mc_res["median_profit"], currency))
        with mc_c3:
            st.metric("Probability of Operating Loss", f"{mc_res['probability_of_loss_pct']:.1f}%")

    with tab_sens:
        st.markdown("### Deterministic Two-Way Sensitivity Grid")
        st.write("Matrix showing projected operating profit across simultaneous revenue and expense shocks.")

        sens_df = run_sensitivity_analysis(base_revenue=base_rev, base_expenses=base_exp)
        
        # Format table with currency
        disp_sens = sens_df.copy()
        for col in disp_sens.columns[1:]:
            disp_sens[col] = disp_sens[col].apply(lambda x: format_currency(x, currency, abbreviate=True))

        st.dataframe(disp_sens, use_container_width=True)
