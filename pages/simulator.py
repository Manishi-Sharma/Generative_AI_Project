"""
Page: Butterfly Effect Simulator (Core Module)
Interactive simulation of mathematical financial ripple effects using NetworkX,
matrix transmission (delta_next = A @ delta_current), feedback damping,
and NVIDIA Nemotron AI synthesis.
"""

from typing import Any, Dict
import streamlit as st
import pandas as pd
from database.connection import get_db_context
from database.models import Scenario
from modules.butterfly_engine import ButterflyEngine, NODES
from modules.financial_data import get_latest_financial_summary
from modules.nvidia_client import nvidia_client
from utils.calculations import format_currency
from utils.visualisations import (
    plot_network_dependency_graph,
    plot_multi_stage_butterfly_ripple,
)


def render_simulator_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 🦋 The Financial Butterfly Effect Simulator")
    st.markdown(
        f"**Entity:** `{current_org.name}` | "
        "Mathematical Simulation of Interconnected Micro-Decisions on Long-Term Corporate Health"
    )

    with get_db_context() as db:
        summary = get_latest_financial_summary(db, current_org.id)

    currency = current_org.currency
    base_rev = summary["total_revenue"] or 30_000_000.0
    base_exp = summary["total_expenses"] or 22_000_000.0
    base_cash = summary["cash_reserves"] or 15_000_000.0

    # Sidebar / Top Parameters
    st.markdown("### 🎛️ Configure Strategic Policy Levers")
    st.write("Adjust the financial policy levers below to observe cascading first- and second-order ripple effects across the entire enterprise.")

    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.markdown("##### Operational & Cost Control")
        opex_pct = st.slider("Operating Expenses (%)", min_value=-30.0, max_value=20.0, value=-2.0, step=0.5,
                             help="E.g. -2% represents a 2% cost reduction directive.")
        marketing_pct = st.slider("Marketing & Acquisition Spend (%)", min_value=-30.0, max_value=40.0, value=0.0, step=1.0)

    with col_l2:
        st.markdown("##### Capital Allocation & Technology")
        inv_pct = st.slider("Investment Capital Allocation (%)", min_value=-20.0, max_value=50.0, value=5.0, step=1.0)
        rd_pct = st.slider("R&D & Engineering Spending (%)", min_value=-20.0, max_value=50.0, value=5.0, step=1.0)

    with col_l3:
        st.markdown("##### Workforce & Operational Capacity")
        prod_pct = st.slider("Direct Productivity / Tooling (%)", min_value=-15.0, max_value=25.0, value=0.0, step=1.0)
        scenario_mode = st.selectbox("Macroeconomic Elasticity Scenario", ["Baseline", "Optimistic (+20% Multiplier)", "Pessimistic (-20% Drag)"])

    # Map scenario multiplier
    multiplier = 1.0
    if "Optimistic" in scenario_mode:
        multiplier = 1.20
    elif "Pessimistic" in scenario_mode:
        multiplier = 0.80

    # Build shock dictionary
    initial_shocks = {}
    if opex_pct != 0:
        initial_shocks["Operating Expenses"] = opex_pct / 100.0
    if marketing_pct != 0:
        initial_shocks["Marketing"] = marketing_pct / 100.0
    if inv_pct != 0:
        initial_shocks["Investment Capital"] = inv_pct / 100.0
    if rd_pct != 0:
        initial_shocks["Research and Development"] = rd_pct / 100.0
    if prod_pct != 0:
        initial_shocks["Employee Productivity"] = prod_pct / 100.0

    # Run Simulation
    engine = ButterflyEngine()
    sim_results = engine.calculate_ripple(
        initial_shocks=initial_shocks,
        scenario_multiplier=multiplier,
        damping_factor=0.85,
        max_periods=5,
    )

    st.markdown("---")

    # 1. Delta Overview Cards
    st.markdown("### 📊 Direct vs Cascading Ripple Outcome (Year 5 Projected)")
    deltas = sim_results["final_5yr_deltas"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        rev_d = deltas.get("Revenue", 0.0)
        st.metric(
            label="Projected Revenue Delta",
            value=f"{rev_d:+.2%}",
            delta=format_currency(base_rev * rev_d, currency, abbreviate=True),
        )
    with c2:
        exp_d = deltas.get("Operating Expenses", 0.0)
        st.metric(
            label="Operating Expenses Delta",
            value=f"{exp_d:+.2%}",
            delta=format_currency(base_exp * exp_d, currency, abbreviate=True),
            delta_color="inverse",
        )
    with c3:
        cash_d = deltas.get("Cash Reserves", 0.0)
        st.metric(
            label="Cash Reserves Delta",
            value=f"{cash_d:+.2%}",
            delta=format_currency(base_cash * cash_d, currency, abbreviate=True),
        )
    with c4:
        prod_d = deltas.get("Employee Productivity", 0.0)
        st.metric(
            label="Worker Productivity Delta",
            value=f"{prod_d:+.2%}",
            delta="Capacity Multiplier",
        )

    # 2. Interactive Charts Section
    tab_graph, tab_trajectory, tab_chains = st.tabs([
        "🕸️ Directed Dependency Network Graph",
        "📈 Multi-Period Trajectory (T+1 to T+5)",
        "🔗 Causal Transmission Chain Explanation",
    ])

    with tab_graph:
        st.plotly_chart(
            plot_network_dependency_graph(engine.graph, impact_deltas=deltas),
            use_container_width=True,
        )
        st.caption("🟢 Green Nodes: Favorable Expansion | 🔴 Red Nodes: Contraction / Stress | 🔵 Cyan Nodes: Neutral Baseline")

    with tab_trajectory:
        st.plotly_chart(
            plot_multi_stage_butterfly_ripple(sim_results["period_names"], sim_results["trajectories"]),
            use_container_width=True,
        )

    with tab_chains:
        st.markdown("#### Mathematical Transmission Paths")
        chains = sim_results["causal_chains"]
        if not chains:
            st.info("No policy shocks configured. Adjust sliders to observe transmission paths.")
        else:
            for step in chains:
                if "Decision:" in step:
                    st.markdown(f"**{step}**")
                elif "↳ Direct Effect:" in step:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{step}")
                else:
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*{step}*")

    # 3. Trade-offs: Positive and Negative Consequences
    st.markdown("### ⚖️ Systematic Trade-Off Analysis")
    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.markdown("#### ✅ Favorable Consequences")
        positives = sim_results["positive_consequences"]
        if positives:
            for p in positives:
                st.markdown(f"- **{p}**")
        else:
            st.write("No major positive shifts observed.")

    with col_neg:
        st.markdown("#### ⚠️ Adverse Consequences & Friction Risks")
        negatives = sim_results["negative_consequences"]
        if negatives:
            for n in negatives:
                st.markdown(f"- <span style='color: #f43f5e;'>**{n}**</span>", unsafe_allow_html=True)
        else:
            st.write("No severe negative repercussions observed under current parameters.")

    # 4. NVIDIA AI Executive Briefing
    st.markdown("### 🤖 NVIDIA Nemotron AI Board Synthesis")
    if st.button("Generate Executive Board Briefing (NVIDIA NIM)", type="primary"):
        with st.spinner("NVIDIA Nemotron synthesizing multi-stage mathematical ripple implications..."):
            ai_resp = nvidia_client.explain_butterfly_effect(
                initial_shocks=initial_shocks,
                ripple_results=sim_results,
                org_name=current_org.name,
            )
            st.markdown(ai_resp["response"])
            if ai_resp["was_fallback"]:
                st.caption(f"⚡ Generated via: `{ai_resp['model']}` (High-precision deterministic engine)")
            else:
                st.caption(f"🧠 Powered by NVIDIA NIM (`{ai_resp['model']}`)")

    # 5. Save as Scenario
    with st.expander("💾 Save Current Configuration as Named Scenario"):
        with st.form("form_save_scenario"):
            sc_name = st.text_input("Scenario Name", placeholder="e.g. 2026 Conservative OPEX & Innovation Shift")
            sc_type = st.selectbox("Category", ["Optimistic", "Baseline", "Pessimistic", "Custom Policy"])
            sc_desc = st.text_area("Strategic Scenario Notes")
            save_btn = st.form_submit_button("Save Scenario")

            if save_btn:
                if not sc_name.strip():
                    st.error("Scenario name is required.")
                else:
                    import json
                    with get_db_context() as db:
                        new_sc = Scenario(
                            org_id=current_org.id,
                            name=sc_name.strip(),
                            scenario_type=sc_type,
                            description=sc_desc.strip(),
                            parameter_changes_json=json.dumps(initial_shocks),
                        )
                        db.add(new_sc)
                        db.commit()
                    st.success(f"Scenario '{sc_name}' stored successfully!")
