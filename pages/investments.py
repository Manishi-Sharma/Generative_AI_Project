"""
Page: Investment Management
Manages investment portfolio allocations, calculates ROI, NPV, simple and
compound interest projections, and conducts scenario return analyses.
"""

from typing import Any
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from modules.investment import (
    get_investments_dataframe,
    analyze_investment_portfolio,
    add_investment,
)
from modules.authentication import check_permission
from utils.calculations import format_currency
from utils.visualisations import plot_investment_allocation


def render_investments_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 📈 Investment Portfolio & Capital Allocation")
    st.markdown(f"**Entity:** `{current_org.name}` | Capital Growth & Yield Strategy")

    with get_db_context() as db:
        inv_analysis = analyze_investment_portfolio(db, current_org.id)
        df_inv = get_investments_dataframe(db, current_org.id)

    currency = current_org.currency

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Invested Capital", format_currency(inv_analysis["total_invested"], currency, abbreviate=True))
    with c2:
        st.metric("Weighted Expected Return", f"{inv_analysis['weighted_return'] * 100:.2f}% p.a.")
    with c3:
        st.metric("Portfolio Net Present Value (NPV)", format_currency(inv_analysis["portfolio_npv"], currency, abbreviate=True))
    with c4:
        st.metric("Active Holdings", f"{inv_analysis['active_count']} Assets")

    st.caption("⚠️ **Notice:** Expected returns and NPV figures are mathematical projections based on management assumptions and do not represent guaranteed financial results.")
    st.markdown("---")

    tab_overview, tab_add, tab_scenarios = st.tabs([
        "📊 Portfolio Overview & Allocations",
        "➕ Add Capital Investment",
        "🔮 Return Scenario Stress-Test"
    ])

    with tab_overview:
        row1, row2 = st.columns([1.2, 1.0])
        with row1:
            if df_inv.empty:
                st.info("No active investments recorded.")
            else:
                display_inv = df_inv.copy()
                for c in ["amount", "simple_interest", "compound_interest", "projected_value", "npv"]:
                    display_inv[c] = display_inv[c].apply(lambda x: format_currency(x, currency))
                display_inv["expected_roi"] = display_inv["expected_roi"].apply(lambda x: f"{x:.1f}%")

                cols_show = [
                    "name", "category", "amount", "return_pct_str", "duration_years",
                    "risk_category", "projected_value", "expected_roi", "npv"
                ]
                st.dataframe(display_inv[cols_show], use_container_width=True)

        with row2:
            st.plotly_chart(plot_investment_allocation(df_inv), use_container_width=True)

    with tab_add:
        if not check_permission(current_user.role, "manage_investments"):
            st.warning("Only Financial Managers or Administrators can register new investments.")
        else:
            st.markdown("### Record New Investment Deployment")
            with st.form("form_add_inv"):
                col_a, col_b = st.columns(2)
                with col_a:
                    inv_name = st.text_input("Investment / Project Name", placeholder="e.g. Solar Rooftop Energy Array")
                    category = st.selectbox("Asset Class", [
                        "Infrastructure & Plant",
                        "Research & Development",
                        "Equities & Private Placements",
                        "Debt & Fixed Income",
                        "Technology & Software Automation",
                        "Treasury Liquid Funds",
                    ])
                    amount = st.number_input("Capital Committed (₹)", min_value=10000.0, step=100000.0, value=5000000.0)

                with col_b:
                    expected_return = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=40.0, value=12.5, step=0.5) / 100.0
                    duration = st.number_input("Holding Horizon (Years)", min_value=1, max_value=25, value=4)
                    risk_cat = st.selectbox("Risk Categorisation", ["Low", "Moderate", "High", "Speculative"])
                    inv_date = st.date_input("Deployment Date")

                notes = st.text_input("Investment Notes & Objectives", placeholder="e.g. Expected to lower factory utility bills by 22% after commissioning.")
                submit_inv = st.form_submit_button("Record Capital Allocation", type="primary")

                if submit_inv:
                    if not inv_name.strip():
                        st.error("Investment name is required.")
                    else:
                        inv_data = {
                            "name": inv_name,
                            "category": category,
                            "amount": amount,
                            "expected_return_rate": expected_return,
                            "duration_years": duration,
                            "risk_category": risk_cat,
                            "investment_date": str(inv_date),
                            "notes": notes,
                        }
                        with get_db_context() as db:
                            success, inv_obj, msg = add_investment(db, current_org.id, inv_data)
                        if success:
                            st.success(f"Investment '{inv_name}' successfully added to portfolio!")
                            st.rerun()
                        else:
                            st.error(msg)

    with tab_scenarios:
        st.markdown("### Scenario-Based Portfolio Return Projections")
        st.write("Evaluating portfolio terminal value under varying macroeconomic yield environments.")

        projections = inv_analysis.get("scenario_projections", {})
        if not projections:
            st.info("No active investments to evaluate.")
        else:
            sc_cols = st.columns(3)
            cases = [
                ("bear_case", sc_cols[0], "📉", "#f43f5e"),
                ("base_case", sc_cols[1], "📊", "#3b82f6"),
                ("bull_case", sc_cols[2], "🚀", "#10b981"),
            ]
            for key, col, icon, color in cases:
                case_data = projections.get(key, {})
                with col:
                    st.markdown(f"""
                    <div style="background-color: #1c2541; border: 1px solid #273549; border-radius: 10px; padding: 16px;">
                        <div style="font-size: 20px;">{icon}</div>
                        <div style="font-weight: 700; color: #e2e8f0; margin-top: 6px;">{case_data.get('label', '')}</div>
                        <div style="font-size: 26px; font-weight: 700; color: {color}; margin-top: 10px;">
                            {format_currency(case_data.get('projected_total', 0), currency, abbreviate=True)}
                        </div>
                        <div style="font-size: 12px; color: #94a3b8; margin-top: 6px;">
                            Total Net Yield: {format_currency(case_data.get('projected_yield', 0), currency, abbreviate=True)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
