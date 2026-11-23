import streamlit as st
from integrations.nvidia_nemotron import NemotronExplainer
from modules.report_generator import PDFReportGenerator
from database.connection import SessionLocal
from database.models import AIReport

def render_ai_reports():
    org = st.session_state.get("selected_org")
    if not org:
        st.warning("⚠️ No organisation selected. Please start in **Organisation Search**.")
        return

    sim_result = st.session_state.get("simulation_result")
    if not sim_result:
        st.warning("⚠️ No simulation has been executed yet. Please run a scenario in **Butterfly Effect Analysis** first.")
        return

    st.markdown(f"## 🤖 NVIDIA Nemotron AI Insights & Executive Report")
    st.caption("AI-powered financial interpretation using **NVIDIA Nemotron 120B** via NVIDIA NIM API.")

    explainer = NemotronExplainer()

    # Model status badge
    st.markdown(f"""
    <div style="background-color: #001F54; padding: 12px 18px; border-radius: 8px; border: 1px solid #1282A2; margin-bottom: 16px;">
        <span style="color: #00F5D4; font-weight: bold;">● Active Model:</span> 
        <span style="color: #FEFCFB;">nvidia/nemotron-3.5-super-vl-120b-a12b</span> | 
        <span style="color: #A0C4E2;">API Mode: {'NVIDIA NIM API Connected' if explainer.is_configured() else 'Deterministic Analytical Engine (No API key set)'}</span>
    </div>
    """, unsafe_allow_html=True)

    fin_records = st.session_state.get("financial_records", [])
    calculations = st.session_state.get("calculations", {})

    gen_col1, gen_col2 = st.columns([3, 1])
    with gen_col1:
        st.write(f"Generating comprehensive ripple-effect interpretation for **{org.get('name')}**...")
    with gen_col2:
        generate_btn = st.button("Generate AI Insights", type="primary", use_container_width=True)

    if generate_btn or not st.session_state.get("ai_explanation"):
        with st.spinner("Invoking NVIDIA Nemotron to interpret simulation dynamics and risks..."):
            ai_text = explainer.explain_simulation(
                org_name=org.get("name"),
                company_profile=org,
                retrieved_financials=fin_records,
                calculations=calculations,
                simulation_result=sim_result
            )
            st.session_state.ai_explanation = ai_text

            # Persist AI report to DB
            user = st.session_state.get("user")
            if user:
                session = SessionLocal()
                try:
                    rep = AIReport(
                        scenario_id=1,
                        user_id=user.id,
                        org_id=org["id"],
                        content=ai_text
                    )
                    session.add(rep)
                    session.commit()
                except Exception:
                    session.rollback()
                finally:
                    session.close()

    ai_text = st.session_state.get("ai_explanation", "")
    if ai_text:
        st.markdown("### 📋 Executive Financial Analysis")
        st.markdown(ai_text)

        st.markdown("---")
        st.markdown("### 📥 Download Formal Academic Report (PDF)")
        st.caption("Generate a structured audit report including organisation information, verified disclosures, ripple matrix, and AI insights.")

        with st.spinner("Compiling PDF report..."):
            pdf_bytes = PDFReportGenerator.generate_pdf(
                org_data=org,
                financial_records=fin_records,
                calculations=calculations,
                simulation_result=sim_result,
                ai_analysis_text=ai_text
            )

        filename = f"Financial_Butterfly_Effect_{org.get('name').replace(' ', '_')}_{sim_result.get('initial_variable').replace(' ', '_')}.pdf"
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary"
        )
