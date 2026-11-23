import streamlit as st
from modules.organisation_search import OrganisationSearchEngine
from modules.public_data_collector import PublicDataCollector
from modules.financial_calculations import FinancialCalculator

def render_organisation_search():
    st.markdown("## 🔍 Organisation Discovery & Search")
    st.markdown(
        "Search for **any real organisation, public corporation, private enterprise, or non-profit** worldwide. "
        "The system discovers official regulatory filings (e.g. U.S. SEC EDGAR) and public web records."
    )

    search_engine = OrganisationSearchEngine()
    collector = PublicDataCollector()

    # Search Bar
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Enter Organisation Name or Ticker:",
            placeholder="e.g. Infosys, Microsoft, Reliance Industries, Apple, Siemens...",
            key="org_search_input"
        )
    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("Search Public Sources", use_container_width=True, type="primary")

    if search_btn and query.strip():
        with st.spinner(f"Searching public registries and web records for '{query}'..."):
            candidates = search_engine.search(query)
            st.session_state.search_candidates = candidates
            st.session_state.last_search_query = query

    # User Search History Section
    user = st.session_state.get("user")
    if user:
        history = search_engine.get_user_search_history(user.id, limit=6)
        if history:
            with st.expander("🕒 Your Recent Searches (Instant Re-load)", expanded=not bool(st.session_state.get("search_candidates"))):
                st.caption("Quickly reload previously fetched financial disclosures without re-querying external APIs:")
                hist_cols = st.columns(min(len(history), 3))
                for h_idx, h_item in enumerate(history[:3]):
                    with hist_cols[h_idx % 3]:
                        st.markdown(f"""
                        <div style="background-color: #001F54; padding: 12px; border-radius: 6px; border: 1px solid #1282A2; margin-bottom: 8px;">
                            <b style="color: #FEFCFB; font-size: 14px;">{h_item['name']}</b><br/>
                            <span style="color: #A0C4E2; font-size: 11px;">{h_item.get('ticker') or 'Unlisted'} • {h_item.get('country') or 'Global'}</span><br/>
                            <span style="color: #8D99AE; font-size: 10px;">Visited: {h_item['searched_at']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("⚡ Instant Load", key=f"hist_load_{h_item['org_id']}", use_container_width=True):
                            with st.spinner(f"Loading saved financial data for {h_item['name']}..."):
                                saved_records = collector.get_saved_financials(h_item['org_id'])
                                metric_values = {
                                    r["metric_name"]: r["value"] for r in saved_records if r.get("value") is not None
                                }
                                calcs = FinancialCalculator.calculate_all(metric_values)
                                st.session_state.selected_org = {
                                    "id": h_item["org_id"],
                                    "name": h_item["name"],
                                    "country": h_item["country"],
                                    "industry": h_item["industry"],
                                    "description": h_item["description"],
                                    "website": h_item["website"],
                                    "ticker": h_item["ticker"],
                                    "stock_exchange": h_item["stock_exchange"],
                                    "is_listed": h_item["is_listed"]
                                }
                                st.session_state.financial_records = saved_records
                                st.session_state.calculations = calcs
                                st.session_state.simulation_result = None
                                st.session_state.ai_explanation = ""
                                search_engine.record_user_search(user.id, h_item["org_id"])
                                st.success(f"Loaded **{h_item['name']}** successfully!")
                                st.rerun()

    candidates = st.session_state.get("search_candidates", [])
    if candidates:
        st.markdown(f"### Discovered Organisations ({len(candidates)} match{'es' if len(candidates) > 1 else ''})")
        st.caption("Please select the correct entity to retrieve verified public financial data:")

        for idx, cand in enumerate(candidates):
            with st.container():
                st.markdown(f"""
                <div style="background-color: #001F54; padding: 16px; border-radius: 8px; border: 1px solid #1282A2; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: #FEFCFB; margin: 0;">{cand.get('name')}</h4>
                        <span style="background-color: #034078; color: #00F5D4; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold;">
                            {cand.get('source', 'Public Record')}
                        </span>
                    </div>
                    <p style="color: #A0C4E2; font-size: 13px; margin: 6px 0;">
                        <b>Country:</b> {cand.get('country', 'Global')} | 
                        <b>Industry:</b> {cand.get('industry', 'General')} | 
                        <b>Ticker / Exchange:</b> {cand.get('ticker') or 'Unlisted'} ({cand.get('stock_exchange') or 'N/A'})
                    </p>
                    <p style="color: #D1D5DB; font-size: 13px; margin: 6px 0;">{cand.get('description', '')}</p>
                </div>
                """, unsafe_allow_html=True)

                select_col1, select_col2 = st.columns([4, 1])
                with select_col2:
                    if st.button(f"Select & Retrieve Data", key=f"select_org_{idx}", type="secondary", use_container_width=True):
                        with st.spinner(f"Retrieving and verifying public disclosures for {cand.get('name')}..."):
                            # Save or get DB record
                            org_record = search_engine.get_or_create_organisation(cand)
                            # Collect financial data
                            fin_records = collector.collect_organisation_financials(org_record, cand.get("cik"))

                            # Extract numeric dictionary for financial calculations
                            metric_values = {
                                r["metric_name"]: r["value"] for r in fin_records if r.get("value") is not None
                            }
                            calcs = FinancialCalculator.calculate_all(metric_values)

                            # Save to session state
                            st.session_state.selected_org = {
                                "id": org_record.id,
                                "name": org_record.name,
                                "country": org_record.country,
                                "industry": org_record.industry,
                                "description": org_record.description,
                                "website": org_record.website,
                                "ticker": org_record.ticker,
                                "stock_exchange": org_record.stock_exchange,
                                "is_listed": org_record.is_listed
                            }
                            st.session_state.financial_records = fin_records
                            st.session_state.calculations = calcs
                            st.session_state.simulation_result = None
                            st.session_state.ai_explanation = ""

                            # Record search in user history
                            user = st.session_state.get("user")
                            if user:
                                search_engine.record_user_search(user.id, org_record.id)

                            st.success(f"Successfully selected **{cand.get('name')}**! Proceed to 'Financial Overview'.")
                            st.rerun()

    # If an organisation is currently selected, show current status
    if st.session_state.get("selected_org"):
        curr = st.session_state.selected_org
        st.markdown("---")
        st.markdown(f"### Currently Active: **{curr.get('name')}**")
        st.info("You can proceed to **Financial Overview** or **Butterfly Effect Analysis** in the sidebar navigation.")
