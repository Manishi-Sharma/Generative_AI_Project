"""
Page: Executive Dashboard
Renders enterprise financial KPIs, balance sheet health score,
revenue vs operating expenses, expense distribution, and recent activity.
"""

from typing import Any
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from modules.financial_data import get_latest_financial_summary, get_financial_dataframe
from modules.financial_analysis import compute_financial_health_score
from modules.investment import analyze_investment_portfolio
from modules.savings import analyze_expense_saving_opportunities
from modules.risk_analysis import evaluate_financial_risks
from utils.calculations import format_currency
from utils.visualisations import (
    plot_revenue_vs_expenses,
    plot_expense_distribution,
    plot_risk_radar,
)


def render_dashboard(org: Any, current_user: Any) -> None:
    st.markdown(f"## 🏛️ Executive Financial Dashboard")
    st.markdown(f"**Entity:** `{org.name}` | **Fiscal Type:** `{org.org_type}` | **Currency:** `{org.currency}`")

    if org.is_synthetic:
        st.info("ℹ️ **Notice:** Demonstration data displayed for this organisation is synthetic and generated for illustrative stress-testing.")

    with get_db_context() as db:
        summary = get_latest_financial_summary(db, org.id)
        df_fin = get_financial_dataframe(db, org.id)
        inv_data = analyze_investment_portfolio(db, org.id)
        savings_data = analyze_expense_saving_opportunities(db, org.id)
        
        # Risk evaluation
        records = list(df_fin.itertuples()) if not df_fin.empty else []
        risks = evaluate_financial_risks(records, None)
        health = compute_financial_health_score(summary)

    if not summary["has_data"]:
        st.warning("No financial records found for this organisation. Navigate to 'Financial Data' to enter records or upload a CSV.")
        return

    # Top KPI Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            label="Total Revenue (LTM)",
            value=format_currency(summary["total_revenue"], org.currency, abbreviate=True),
            delta=f"Margin: {summary['profit_margin']:.1f}%",
        )
    with c2:
        st.metric(
            label="Operating Expenses",
            value=format_currency(summary["total_expenses"], org.currency, abbreviate=True),
            delta=f"Net: {format_currency(summary['net_profit'], org.currency, abbreviate=True)}",
        )
    with c3:
        st.metric(
            label="Liquid Cash Reserves",
            value=format_currency(summary["cash_reserves"], org.currency, abbreviate=True),
            delta=f"Curr Ratio: {summary['current_ratio']:.2f}x",
        )
    with c4:
        st.metric(
            label="Invested Capital",
            value=format_currency(inv_data["total_invested"], org.currency, abbreviate=True),
            delta=f"Yield: {inv_data['weighted_return']*100:.1f}%",
        )

    st.markdown("---")

    # Financial Health Index Banner
    col_health, col_risk = st.columns([1, 1])
    with col_health:
        st.markdown(f"""
        <div style="background-color: #1c2541; border: 1px solid #273549; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
            <div style="color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Balance Sheet Health Score</div>
            <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 6px;">
                <span style="font-size: 38px; font-weight: 700; color: {health['color']};">{health['score']}</span>
                <span style="font-size: 18px; font-weight: 600; color: #e2e8f0;">/ 100</span>
                <span style="background-color: rgba(16, 185, 129, 0.15); color: {health['color']}; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600;">{health['grade']}</span>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #94a3b8;">
                Profitability: {health['breakdown']['Profitability']}/30 &nbsp;|&nbsp; 
                Liquidity: {health['breakdown']['Liquidity']}/30 &nbsp;|&nbsp; 
                Solvency: {health['breakdown']['Solvency']}/20 &nbsp;|&nbsp; 
                Cash Buffer: {health['breakdown']['Cash Buffer']}/20
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_risk:
        st.markdown(f"""
        <div style="background-color: #1c2541; border: 1px solid #273549; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
            <div style="color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Overall Risk Exposure</div>
            <div style="display: flex; align-items: baseline; gap: 12px; margin-top: 6px;">
                <span style="font-size: 38px; font-weight: 700; color: {'#10b981' if risks['overall_risk_score'] < 40 else '#f59e0b' if risks['overall_risk_score'] < 70 else '#f43f5e'};">{risks['overall_risk_score']}</span>
                <span style="font-size: 18px; font-weight: 600; color: #e2e8f0;">/ 100</span>
                <span style="background-color: rgba(244, 63, 94, 0.15); color: #f43f5e; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600;">{risks['risk_tier']}</span>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #94a3b8;">
                Liquidity Risk: {risks['liquidity_risk']}/100 &nbsp;|&nbsp; 
                Debt Risk: {risks['debt_risk']}/100 &nbsp;|&nbsp; 
                Runway: {risks['runway_months']:.1f} Months
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Charts Grid
    row1_c1, row1_c2 = st.columns([1.4, 1.0])
    with row1_c1:
        st.plotly_chart(plot_revenue_vs_expenses(df_fin), use_container_width=True)

    with row1_c2:
        latest_rec = summary.get("latest_record", {})
        st.plotly_chart(plot_expense_distribution(latest_rec), use_container_width=True)

    # Quick Insights Grid
    st.markdown("### 💡 Strategic Operational Highlights")
    q1, q2 = st.columns(2)
    with q1:
        st.markdown(f"""
        **Expense Rationalization Opportunities:**
        - Identified Safe Reductions: **{format_currency(savings_data.get('potential_total_savings', 0), org.currency, abbreviate=True)}**
        - Priority Areas: Non-core admin, power efficiency, and vendor licensing.
        - *Recommendation:* Direct at least 50% of savings into productive capital deployment.
        """)
    with q2:
        st.markdown(f"""
        **Capital Allocation & Ripple Dynamics:**
        - Active Investment Positions: **{inv_data['active_count']}**
        - Expected Weighted Return: **{inv_data['weighted_return']*100:.2f}%**
        - *Butterfly Effect Alert:* Reducing OPEX without reinvestment risks a **2.4% drag** in Year 2 worker productivity.
        """)
