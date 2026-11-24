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

    # Slideable / Scrollable Search History Section
    user = st.session_state.get("user")
    if user:
        history = search_engine.get_user_search_history(user.id, limit=100)
        if history:
            st.markdown("---")
            h_head1, h_head2 = st.columns([3, 1])
            with h_head1:
                st.markdown(f"#### 🕒 Your Search History ({len(history)} saved)")
                st.caption("Scroll / slide inside the box below to view past searches. Click 'Load' to restore or '🗑️' to delete:")
            with h_head2:
                st.write("")
                if st.button("🗑️ Clear All History", key="main_clear_all_history", type="secondary", use_container_width=True):
                    search_engine.clear_all_user_search_history(user.id)
                    st.success("All search history cleared!")
                    st.rerun()

            # Fixed-height scrollable container: slides up/down smoothly without taking over the screen
            with st.container(height=260):
                for h_item in history:
                    c_info, c_load, c_del = st.columns([4, 1.4, 0.8])
                    with c_info:
                        ticker_badge = f" • <span style='color: #00F5D4; font-weight: 600;'>{h_item.get('ticker') or 'Unlisted'}</span>"
                        country_badge = f" <span style='color: #A0C4E2; font-size: 12px;'>({h_item.get('country') or 'Global'})</span>"
                        st.markdown(f"""
                        <div style='margin-bottom: 2px;'>
                            <b style='color: #FEFCFB; font-size: 14px;'>{h_item['name']}</b>{ticker_badge}{country_badge}<br/>
                            <span style='color: #8D99AE; font-size: 11px;'>Visited: {h_item['searched_at']}</span>
                        </div>
                        """, unsafe_allow_html=True)

                    with c_load:
                        is_active = (st.session_state.selected_org and st.session_state.selected_org.get("id") == h_item["org_id"])
                        load_btn_type = "primary" if is_active else "secondary"
                        if st.button("⚡ Load", key=f"main_hist_load_{h_item['history_id']}", type=load_btn_type, use_container_width=True):
                            with st.spinner(f"Loading {h_item['name']}..."):
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
                                st.rerun()

                    with c_del:
                        if st.button("🗑️", key=f"main_hist_del_{h_item['history_id']}", help=f"Delete {h_item['name']} from history", use_container_width=True):
                            search_engine.delete_user_search_entry(user.id, h_item['history_id'])
                            st.rerun()

                    st.markdown("<hr style='margin: 3px 0 6px 0; border: none; border-top: 1px solid rgba(18, 130, 162, 0.2);'>", unsafe_allow_html=True)

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
