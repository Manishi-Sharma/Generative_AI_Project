"""
Page: Savings Optimisation & Expense Reduction
Identifies cost reduction opportunities, models operational consequences
of excessive budget cuts, and simulates reinvestment into productive capital.
"""

from typing import Any
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from modules.savings import (
    analyze_expense_saving_opportunities,
    create_savings_plan,
    get_savings_plans,
    simulate_savings_reinvestment,
)
from modules.organisation import get_organisation_departments
from modules.authentication import check_permission
from utils.calculations import format_currency


def render_savings_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 💰 Savings Optimisation & Cost Rationalisation")
    st.markdown(f"**Entity:** `{current_org.name}` | Disciplined Expense Control & Capital Reinvestment")

    with get_db_context() as db:
        savings_data = analyze_expense_saving_opportunities(db, current_org.id)
        departments = get_organisation_departments(db, current_org.id)
        existing_plans = get_savings_plans(db, current_org.id)

    currency = current_org.currency

    # Overview KPI Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Operating Expenditure (LTM)", format_currency(savings_data.get("annual_operating_expenses", 0), currency, abbreviate=True))
    with c2:
        st.metric("Potential Annual Cost Reductions", format_currency(savings_data.get("potential_total_savings", 0), currency, abbreviate=True))
    with c3:
        st.metric("Active Savings Programs", f"{len(existing_plans)} Directives")

    st.markdown("---")

    tab_recs, tab_sim, tab_plans = st.tabs([
        "🔍 Rationalisation Diagnostics & Trade-offs",
        "🌱 Reinvestment & Compounding Simulator",
        "📑 Active Savings Directives"
    ])

    with tab_recs:
        st.markdown("### Cost Driver Analysis & Recommended Safe Reductions")
        st.write("Identifies high-expenditure cost pools where reduction can be achieved without compromising frontline operational throughput.")

        shares = savings_data.get("category_shares", {})
        if shares:
            st.markdown("#### Expense Pool Distribution")
            cols = st.columns(min(len(shares), 4))
            for i, (cat, val) in enumerate(shares.items()):
                with cols[i % len(cols)]:
                    st.markdown(f"""
                    <div style="background-color: #1c2541; border: 1px solid #273549; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">{cat}</div>
                        <div style="font-size: 18px; font-weight: 700; color: #e2e8f0; margin-top: 4px;">{format_currency(val['amount'], currency, abbreviate=True)}</div>
                        <div style="font-size: 11px; color: #10b981; font-weight: 600;">{val['share_pct']}% of OPEX</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("#### Recommended Savings Actions")
        recs = savings_data.get("recommendations", [])
        if not recs:
            st.info("Current operational expense distribution is balanced; no excessive overhead concentrations detected.")
        else:
            for r in recs:
                st.markdown(f"""
                <div style="background-color: #1c2541; border-left: 4px solid #f59e0b; border-radius: 6px; padding: 14px; margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 16px; font-weight: 700; color: #e2e8f0;">{r['category']}</span>
                        <span style="background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">Target: -{r['recommended_cut_pct']}%</span>
                    </div>
                    <div style="color: #10b981; font-weight: 600; font-size: 14px; margin-top: 6px;">
                        Estimated Annual Savings: {format_currency(r['potential_annual_savings'], currency)}
                    </div>
                    <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">{r['rationale']}</div>
                    <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;"><b>Operational Hazard Assessment:</b> {r['operational_risk']}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab_sim:
        st.markdown("### Interactive Savings Reinvestment Simulator")
        st.write("Calculate the multi-year compound value created when freed cash is divided between liquid emergency reserves and high-ROI productive investments.")

        sim_c1, sim_c2 = st.columns([1, 1.4])
        with sim_c1:
            annual_saved = st.number_input(
                "Annual Capital Freed via Savings (₹)",
                min_value=100000.0,
                max_value=100000000.0,
                value=float(savings_data.get("potential_total_savings", 2500000.0) or 2500000.0),
                step=100000.0
            )
            reinvest_ratio = st.slider("Allocation to Productive Reinvestment / R&D (%)", min_value=10, max_value=90, value=60, step=5)
            reserve_ratio = 100 - reinvest_ratio
            st.write(f"Allocation to Liquid Emergency Reserves: **{reserve_ratio}%**")

            reinvest_roi = st.slider("Expected Productive Project Yield (%)", min_value=5.0, max_value=25.0, value=12.0, step=0.5) / 100.0
            reserve_int = st.slider("Liquid Treasury Deposit Rate (%)", min_value=3.0, max_value=9.0, value=6.0, step=0.5) / 100.0

        with sim_c2:
            sim_df = simulate_savings_reinvestment(
                annual_savings=annual_saved,
                reinvestment_pct=reinvest_ratio,
                emergency_reserve_pct=reserve_ratio,
                years=5,
                reinvestment_roi_rate=reinvest_roi,
                reserve_interest_rate=reserve_int,
            )

            # Display simulation results
            disp_sim = sim_df.copy()
            for col in ["Annual Savings", "Reinvested Capital", "Emergency Reserves", "Cumulative Returns", "Total Value Created"]:
                disp_sim[col] = disp_sim[col].apply(lambda x: format_currency(x, currency, abbreviate=True))

            st.dataframe(disp_sim, use_container_width=True)
            
            terminal_val = sim_df["Total Value Created"].iloc[-1]
            st.success(f"**5-Year Enterprise Value Created:** {format_currency(terminal_val, currency)} (vs simple cumulative savings of {format_currency(annual_saved * 5, currency)})")

    with tab_plans:
        st.markdown("### Active & Proposed Savings Plans")
        if existing_plans:
            plan_data = [{
                "Plan Name": p.name,
                "Target Reduction (%)": f"{p.target_reduction_pct:.1f}%",
                "Target Amount": format_currency(p.target_reduction_amount, currency),
                "Reinvestment Split": f"{p.reinvestment_pct:.0f}% Reinvest / {p.emergency_reserve_pct:.0f}% Reserve",
                "Operational Risk Score": f"{p.operational_risk_score:.0f}/100",
                "Status": p.status,
            } for p in existing_plans]
            st.dataframe(plan_data, use_container_width=True)
        else:
            st.info("No formal savings programs registered yet.")

        if check_permission(current_user.role, "manage_savings_plans"):
            with st.expander("➕ Register New Savings Directive"):
                with st.form("form_create_savings_plan"):
                    p_name = st.text_input("Savings Initiative Name", placeholder="e.g. Facilities Energy Audit & Solar Adoption")
                    dept_map = {d.id: d.name for d in departments}
                    dept_map[0] = "Enterprise-Wide (All Departments)"
                    target_dept = st.selectbox("Department", options=list(dept_map.keys()), format_func=lambda x: dept_map[x])
                    
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        target_pct = st.slider("Target Expense Reduction (%)", min_value=1.0, max_value=35.0, value=5.0, step=0.5)
                        target_amt = st.number_input("Target Annual Amount (₹)", min_value=50000.0, step=100000.0, value=1500000.0)
                    with col_p2:
                        reinvest_split = st.slider("Reinvestment Allocation (%)", min_value=10, max_value=90, value=60, step=5)
                        reserve_split = 100 - reinvest_split

                    plan_notes = st.text_area("Implementation Rationale & Safeguards", placeholder="Detail operational limits so productivity is not harmed...")
                    submit_plan = st.form_submit_button("Formulate Savings Directive", type="primary")

                    if submit_plan:
                        if not p_name.strip():
                            st.error("Plan name is required.")
                        else:
                            with get_db_context() as db:
                                success, plan_obj, msg = create_savings_plan(
                                    db=db,
                                    org_id=current_org.id,
                                    name=p_name,
                                    department_id=target_dept if target_dept != 0 else None,
                                    target_reduction_pct=target_pct,
                                    target_reduction_amount=target_amt,
                                    reinvestment_pct=reinvest_split,
                                    emergency_reserve_pct=reserve_split,
                                    notes=plan_notes,
                                )
                            if success:
                                st.success("Savings directive formulated!")
                                st.rerun()
                            else:
                                st.error(msg)
