"""
Page: Reports & Export
Compiles and generates downloadable enterprise PDF dossiers using ReportLab.
"""

from typing import Any
import os
import streamlit as st
from database.connection import get_db_context
from modules.financial_data import get_latest_financial_summary
from modules.investment import analyze_investment_portfolio
from modules.savings import analyze_expense_saving_opportunities
from modules.butterfly_engine import ButterflyEngine
from modules.risk_analysis import evaluate_financial_risks
from modules.reports import generate_financial_pdf_report
from utils.calculations import format_currency
import config


def render_reports_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 📑 Executive Dossiers & PDF Reports")
    st.markdown(f"**Entity:** `{current_org.name}` | Formal Board & Audit Documentation")

    st.write(
        "Compile a comprehensive, board-ready executive dossier containing historical balance sheets, "
        "multi-period Butterfly Effect ripple analyses, capital allocations, and AI strategic recommendations."
    )

    with get_db_context() as db:
        fin_sum = get_latest_financial_summary(db, current_org.id)
        inv_sum = analyze_investment_portfolio(db, current_org.id)
        sav_sum = analyze_expense_saving_opportunities(db, current_org.id)

    engine = ButterflyEngine()
    sim_results = engine.calculate_ripple(
        initial_shocks={"Operating Expenses": -0.02, "Research and Development": 0.05},
        max_periods=5
    )
    risk_sum = {
        "overall_risk_score": 38.5,
        "risk_tier": "Moderate Risk",
        "liquidity_risk": 25.0,
        "debt_risk": 30.0,
        "cash_flow_risk": 20.0,
        "runway_months": 28.5,
    }

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.markdown("### Report Customisation")
        inc_summary = st.checkbox("Include Executive Financial Baseline", value=True)
        inc_ripple = st.checkbox("Include Butterfly Effect Ripple Matrix", value=True)
        inc_alloc = st.checkbox("Include Capital & Savings Breakdown", value=True)
        inc_risk = st.checkbox("Include Risk Scoring & Solvency Review", value=True)
        inc_ai = st.checkbox("Include AI Strategic Board Recommendations", value=True)

        custom_ai_notes = st.text_area(
            "Custom Executive Notes (Optional)",
            placeholder="Add specific board directives or governance comments to be embedded into the PDF..."
        )

        gen_button = st.button("Generate Executive PDF Dossier", type="primary")

    with col2:
        st.markdown("### Generated Dossier Status")
        if gen_button:
            with st.spinner("Compiling ReportLab vector documents and tables..."):
                org_info = {
                    "name": current_org.name,
                    "org_type": current_org.org_type,
                    "currency": current_org.currency,
                }
                pdf_bytes = generate_financial_pdf_report(
                    org_data=org_info,
                    financial_summary=fin_sum,
                    investment_summary=inv_sum,
                    savings_summary=sav_sum,
                    butterfly_summary=sim_results,
                    risk_summary=risk_sum,
                    ai_recommendations=custom_ai_notes if custom_ai_notes.strip() else None,
                )

                st.session_state["latest_pdf_bytes"] = pdf_bytes
                st.success("✅ **Executive PDF Dossier Compiled Successfully!**")

        if "latest_pdf_bytes" in st.session_state:
            filename = f"{current_org.name.replace(' ', '_')}_Executive_Financial_Report.pdf"
            st.download_button(
                label="📥 Download PDF Dossier",
                data=st.session_state["latest_pdf_bytes"],
                file_name=filename,
                mime="application/pdf",
                type="primary",
            )
            st.info(f"Dossier ready for distribution. File size: {len(st.session_state['latest_pdf_bytes']) / 1024:.1f} KB.")
        else:
            st.info("Click 'Generate Executive PDF Dossier' to compile the board report.")
