import streamlit as st
import pandas as pd
from modules.butterfly_engine import ButterflyEffectEngine
from utils.formatting import format_currency
from database.connection import SessionLocal
from database.models import Scenario, SimulationResult

def render_butterfly_analysis():
    org = st.session_state.get("selected_org")
    if not org:
        st.warning("⚠️ No organisation selected. Please select an organisation in **Organisation Search** first.")
        return

    st.markdown(f"## 🦋 The Financial Butterfly Effect: **{org.get('name')}**")
    st.markdown(
        "> *“A small hypothetical perturbation in a single corporate financial variable creates "
        "cascading direct and indirect ripple effects across the entire enterprise financial network.”*"
    )

    # Disclaimer Callout
    st.info(
        "ℹ️ **Simulation Modeling Notice:** This scenario is purely a hypothetical simulation for educational and strategic analysis. "
        "It must NEVER be characterized as an actual management decision or announcement by the target organisation."
    )

    engine = ButterflyEffectEngine()

    # Scenario Input Interface
    st.markdown("### 1. Configure Hypothetical Financial Decision")
    c1, c2, c3 = st.columns([2, 2, 2])

    with c1:
        variable = st.selectbox(
            "Select Financial Variable to Perturb:",
            options=engine.VARIABLES,
            index=1, # Operating Expenses by default
            help="Choose the initial variable where the strategic or operational decision occurs."
        )

    with c2:
        change_pct = st.number_input(
            "Hypothetical Change Percentage (%):",
            min_value=-90.0,
            max_value=300.0,
            value=-5.0,
            step=1.0,
            help="E.g., -5.0 for a 5% cost reduction, or +10.0 for a 10% revenue expansion."
        )

    with c3:
        time_horizon = st.selectbox(
            "Evaluation Time Horizon:",
            options=["1 Quarter", "2 Quarters", "1 Year", "2 Years", "3 Years", "5 Years"],
            index=2 # 1 Year
        )

    # Prepare baselines from verified retrieved financial records
    fin_records = st.session_state.get("financial_records", [])
    baselines = {}
    for r in fin_records:
        if r.get("value") is not None:
            baselines[r.get("metric_name")] = r.get("value")
            # Map common aliases
            if r.get("metric_name") == "Borrowings (Debt)":
                baselines["Debt"] = r.get("value")
            elif r.get("metric_name") == "Cash and Cash Equivalents":
                baselines["Cash Reserves"] = r.get("value")
            elif r.get("metric_name") == "Operating Cash Flow":
                baselines["Cash Flow"] = r.get("value")

    sim_btn = st.button("🚀 Run Butterfly Effect Ripple Simulation", type="primary", use_container_width=True)

    if sim_btn:
        with st.spinner("Computing multi-order matrix propagation and dependency graph..."):
            sim_result = engine.simulate(
                initial_var=variable,
                initial_change_pct=change_pct,
                time_horizon=time_horizon,
                dampening=0.60,
                baselines=baselines
            )
            st.session_state.simulation_result = sim_result
            # Reset previous AI explanation so user generates fresh for new scenario
            st.session_state.ai_explanation = ""

            # Persist scenario to DB
            user = st.session_state.get("user")
            if user:
                session = SessionLocal()
                try:
                    sc = Scenario(
                        user_id=user.id,
                        org_id=org["id"],
                        variable_name=variable,
                        change_pct=change_pct,
                        time_horizon=time_horizon,
                        rationale=f"Hypothetical simulation of {change_pct:+.2f}% on {variable}"
                    )
                    session.add(sc)
                    session.commit()
                    session.refresh(sc)

                    for v_name, res in sim_result["variable_results"].items():
                        sr = SimulationResult(
                            scenario_id=sc.id,
                            step=1,
                            variable_name=v_name,
                            baseline_value=res.get("baseline_value"),
                            simulated_value=res.get("simulated_value"),
                            delta_pct=res.get("cumulative_delta_pct", 0.0),
                            rationale=f"Cumulative shift: {res.get('cumulative_delta_pct', 0.0):+.2f}%"
                        )
                        session.add(sr)
                    session.commit()
                except Exception as e:
                    session.rollback()
                finally:
                    session.close()

            st.success("Simulation computed successfully!")

    # Display Simulation Results
    sim_result = st.session_state.get("simulation_result")
    if sim_result:
        st.markdown("---")
        st.markdown("### 2. Directed Ripple-Effect Transmission Network")
        st.caption("Visualizing how the initial shock cascades through corporate dependencies. Node color indicates cumulative shift (Teal: Positive, Red: Negative, Purple: Root shock).")

        fig_net = engine.generate_plotly_network(sim_result)
        st.plotly_chart(fig_net, use_container_width=True)

        st.markdown("---")
        st.markdown("### 3. Baseline vs Simulated Financial Comparison")
        fig_comp = engine.generate_comparison_chart(sim_result)
        st.plotly_chart(fig_comp, use_container_width=True)

        # Positive vs Negative Consequences
        st.markdown("---")
        st.markdown("### 4. Direct & Indirect Consequence Classification")
        pos_col, neg_col = st.columns(2)

        with pos_col:
            st.markdown("#### 🟢 Potential Positive Consequences")
            pos_list = sim_result.get("positive_consequences", [])
            if pos_list:
                for item in pos_list:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No major positive shifts identified under current parameters.")

        with neg_col:
            st.markdown("#### 🔴 Potential Risks & Negative Consequences")
            neg_list = sim_result.get("negative_consequences", [])
            if neg_list:
                for item in neg_list:
                    st.markdown(f"- **{item}**")
            else:
                st.write("No significant negative deterioration identified under current parameters.")

        # Step by Step Ripple Breakdown
        st.markdown("---")
        st.markdown("### 5. Step-by-Step Propagation Breakdown")
        for step_data in sim_result.get("step_narratives", []):
            with st.expander(f"Order {step_data['step']}: {step_data['title']}", expanded=(step_data['step'] <= 1)):
                impacts = step_data.get("impacts", [])
                if not impacts:
                    st.write("No significant incremental shifts in this step.")
                for imp in impacts:
                    ch_pct = imp.get("change_pct", 0.0)
                    sign = "+" if ch_pct > 0 else ""
                    st.markdown(f"**{imp.get('variable')}** ({sign}{ch_pct:.2f}%)")
                    drivers = imp.get("drivers", [])
                    for d in drivers:
                        st.caption(f"↳ {d}")

        # Comprehensive Numerical Table
        st.markdown("---")
        st.markdown("### 6. Full Financial Variable Impact Matrix")
        table_rows = []
        for v_name, res in sim_result.get("variable_results", {}).items():
            base_val = res.get("baseline_value")
            sim_val = res.get("simulated_value")
            table_rows.append({
                "Financial Variable": v_name,
                "Initial Shock (%)": f"{res.get('initial_delta_pct', 0.0):+.2f}%",
                "Order-1 Direct (%)": f"{res.get('step1_direct_pct', 0.0):+.2f}%",
                "Order-2 Ripple (%)": f"{res.get('step2_ripple_pct', 0.0):+.2f}%",
                "Cumulative Shift (%)": f"{res.get('cumulative_delta_pct', 0.0):+.2f}%",
                "Reported Baseline": f"{base_val:,.1f}" if base_val is not None else "Not Disclosed",
                "Simulated Projection": f"{sim_val:,.1f}" if sim_val is not None else "Indexed Scale"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        # Assumptions
        st.markdown("---")
        st.markdown("### 7. Simulation Assumptions & Bounds")
        for asm in sim_result.get("assumptions", []):
            st.markdown(f"- _{asm}_")

        st.info("💡 You can now proceed to **AI Insights & Reports** to generate an executive interpretation with NVIDIA Nemotron and download a PDF audit report.")
