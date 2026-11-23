import pytest
import uuid
from auth.authentication import create_user, authenticate_user
from modules.organisation_search import OrganisationSearchEngine
from modules.public_data_collector import PublicDataCollector
from modules.financial_calculations import FinancialCalculator
from modules.butterfly_engine import ButterflyEffectEngine
from integrations.nvidia_nemotron import NemotronExplainer
from modules.report_generator import PDFReportGenerator

def test_complete_user_journey():
    # 1. User Creates an Account
    email = f"student_{uuid.uuid4().hex[:6]}@academic.edu"
    pwd = "StrongPassword2026!"
    reg_ok, _, user = create_user(email, pwd, "Academic Researcher")
    assert reg_ok is True
    assert user is not None

    # 2. User Signs In
    auth_ok, _, auth_user = authenticate_user(email, pwd)
    assert auth_ok is True
    assert auth_user.id == user.id

    # 3. User Searches for an Organisation
    search_engine = OrganisationSearchEngine()
    candidates = search_engine.search("Apple")
    assert len(candidates) > 0
    selected_candidate = candidates[0]
    assert "Apple" in selected_candidate["name"]

    # 4. Save/Get Organisation in Database
    org = search_engine.get_or_create_organisation(selected_candidate)
    assert org.id is not None
    assert org.name == selected_candidate["name"]

    # 5. Application Collects Public Financials
    collector = PublicDataCollector()
    fin_records = collector.collect_organisation_financials(org, selected_candidate.get("cik"))
    assert len(fin_records) > 0

    # 6. Verify Availability Statuses
    statuses = {r["status"] for r in fin_records}
    assert "PUBLIC INFORMATION FOUND" in statuses or "NOT PUBLICLY AVAILABLE" in statuses

    # 7. Deterministic Financial Calculations
    metric_values = {r["metric_name"]: r["value"] for r in fin_records if r.get("value") is not None}
    calcs = FinancialCalculator.calculate_all(metric_values)
    assert "Operating Margin" in calcs
    assert "Net Profit Margin" in calcs
    assert "Return on Assets (ROA)" in calcs

    # 8. User enters hypothetical financial change (-5% Operating Expenses)
    engine = ButterflyEffectEngine()
    baselines = {r["metric_name"]: r["value"] for r in fin_records if r.get("value") is not None}
    sim_result = engine.simulate(
        initial_var="Operating Expenses",
        initial_change_pct=-5.0,
        time_horizon="1 Year",
        dampening=0.60,
        baselines=baselines
    )
    assert sim_result["initial_variable"] == "Operating Expenses"
    assert "variable_results" in sim_result
    assert len(sim_result["positive_consequences"]) > 0

    # 9. Verify Plotly Network & Comparison Charts
    fig_net = engine.generate_plotly_network(sim_result)
    assert fig_net is not None
    fig_comp = engine.generate_comparison_chart(sim_result)
    assert fig_comp is not None

    # 10. AI Explanation (NVIDIA Nemotron / Analytical Explainer)
    explainer = NemotronExplainer()
    org_dict = {
        "name": org.name,
        "country": org.country,
        "industry": org.industry,
        "website": org.website,
        "ticker": org.ticker,
        "stock_exchange": org.stock_exchange
    }
    ai_text = explainer.explain_simulation(
        org_name=org.name,
        company_profile=org_dict,
        retrieved_financials=fin_records,
        calculations=calcs,
        simulation_result=sim_result
    )
    assert len(ai_text) > 100
    assert "EXECUTIVE INTERPRETATION" in ai_text.upper() or "BUTTERFLY EFFECT" in ai_text.upper()

    # 11. PDF Report Generation
    pdf_bytes = PDFReportGenerator.generate_pdf(
        org_data=org_dict,
        financial_records=fin_records,
        calculations=calcs,
        simulation_result=sim_result,
        ai_analysis_text=ai_text
    )
    assert len(pdf_bytes) > 1000 # Valid non-empty PDF binary
    assert pdf_bytes.startswith(b"%PDF")
