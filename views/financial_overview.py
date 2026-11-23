import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import STATUS_FOUND, STATUS_NOT_AVAILABLE, STATUS_RESTRICTED
from utils.formatting import format_currency

def render_financial_overview():
    org = st.session_state.get("selected_org")
    if not org:
        st.warning("⚠️ No organisation currently selected. Please use **Organisation Search** first.")
        return

    st.markdown(f"## 📊 Financial Overview: **{org.get('name')}**")

    # Profile Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Jurisdiction / Country", org.get("country") or "Global")
    with col2:
        st.metric("Industry Sector", org.get("industry") or "Enterprise")
    with col3:
        ticker_display = f"{org.get('ticker')} ({org.get('stock_exchange')})" if org.get("ticker") else "Unlisted / Private"
        st.metric("Ticker / Exchange", ticker_display)
    with col4:
        st.metric("Corporate Status", "Publicly Listed" if org.get("is_listed") else "Private / Registry Disclosed")

    st.markdown("---")

    fin_records = st.session_state.get("financial_records", [])
    if not fin_records:
        st.info("No financial disclosures currently retrieved. Return to Organisation Search to retrieve records.")
        return

    # Data Completeness & Status Summary
    found_count = sum(1 for r in fin_records if r.get("status") == STATUS_FOUND)
    not_avail_count = sum(1 for r in fin_records if r.get("status") == STATUS_NOT_AVAILABLE)
    restricted_count = sum(1 for r in fin_records if r.get("status") == STATUS_RESTRICTED)
    total_count = len(fin_records)
    completeness_pct = (found_count / total_count * 100) if total_count > 0 else 0

    st.markdown("### 📈 Data Availability & Source Verification")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Metrics Tracked", total_count)
    with sc2:
        st.metric("Publicly Found", found_count, f"{completeness_pct:.0f}% Coverage")
    with sc3:
        st.metric("Not Available", not_avail_count)
    with sc4:
        st.metric("Private / Restricted", restricted_count)

    # Financial Performance Charts (if metrics available)
    found_metrics = {r["metric_name"]: r["value"] for r in fin_records if r.get("status") == STATUS_FOUND and r.get("value") is not None}

    if found_metrics:
        st.markdown("### 📊 Performance & Capital Structure")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Revenue vs Profitability Chart
            rev_p_metrics = ["Revenue", "Operating Expenses", "Operating Profit", "Net Profit"]
            rev_data = {m: found_metrics[m] for m in rev_p_metrics if m in found_metrics}
            if rev_data:
                fig_rev = go.Figure(data=[
                    go.Bar(
                        x=list(rev_data.keys()),
                        y=list(rev_data.values()),
                        marker_color=["#3A86FF", "#FF006E", "#8338EC", "#00F5D4"]
                    )
                ])
                fig_rev.update_layout(
                    title=dict(text="<b>Income Statement Core Flow</b>", font=dict(color="#FEFCFB")),
                    paper_bgcolor="#0A1128",
                    plot_bgcolor="#001F54",
                    font=dict(color="#FEFCFB"),
                    height=320,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_rev, use_container_width=True)
            else:
                st.info("Income statement flow requires at least one reported profit metric.")

        with chart_col2:
            # Balance Sheet & Liquidity Chart
            bs_metrics = ["Total Assets", "Total Liabilities", "Shareholders' Equity", "Cash and Cash Equivalents", "Borrowings (Debt)"]
            bs_data = {m: found_metrics[m] for m in bs_metrics if m in found_metrics}
            if bs_data:
                fig_bs = go.Figure(data=[
                    go.Bar(
                        x=list(bs_data.keys()),
                        y=list(bs_data.values()),
                        marker_color=["#00B4D8", "#EF233C", "#7209B7", "#06D6A0", "#F77F00"]
                    )
                ])
                fig_bs.update_layout(
                    title=dict(text="<b>Balance Sheet & Liquidity Distribution</b>", font=dict(color="#FEFCFB")),
                    paper_bgcolor="#0A1128",
                    plot_bgcolor="#001F54",
                    font=dict(color="#FEFCFB"),
                    height=320,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_bs, use_container_width=True)
            else:
                st.info("Balance sheet indicators require asset/liability disclosures.")

    # Detailed Verified Metric Breakdown Table
    st.markdown("### 📑 Disclosed Financial Metrics & Lineage")
    table_rows = []
    for r in fin_records:
        val = r.get("value")
        val_str = format_currency(val, r.get("currency", "USD"), r.get("unit", "Absolute")) if val is not None else "—"

        status = r.get("status")
        if status == STATUS_FOUND:
            badge = "🟢 PUBLIC INFORMATION FOUND"
        elif status == STATUS_RESTRICTED:
            badge = "🔴 ACCESS RESTRICTED / PRIVATE"
        else:
            badge = "🟡 NOT PUBLICLY AVAILABLE"

        source_display = r.get("source_name") or "Public Registry"
        if r.get("source_url"):
            source_link = f"[{source_display}]({r.get('source_url')})"
        else:
            source_link = source_display

        table_rows.append({
            "Metric Name": r.get("metric_name"),
            "Reported Value": val_str,
            "Reporting Period": r.get("period", "N/A"),
            "Status": badge,
            "Verified Source": source_link,
            "Extraction Notes": r.get("notes") or ""
        })

    df_table = pd.DataFrame(table_rows)
    st.markdown(df_table.to_markdown(index=False), unsafe_allow_html=True)

    # Deterministic Financial Ratios Section
    calcs = st.session_state.get("calculations", {})
    if calcs:
        st.markdown("---")
        st.markdown("### 🧮 Deterministic Financial Ratio Analysis")
        st.caption("Ratios are mathematically computed from verified disclosures. Missing required inputs are not converted to zero.")

        cols = st.columns(3)
        col_idx = 0
        for ratio_name, info in calcs.items():
            with cols[col_idx % 3]:
                if info.get("status") == "Computed":
                    val_str = f"{info['value']:.2f} {info['unit']}"
                    st.metric(label=ratio_name, value=val_str)
                    st.caption(f"**Formula:** `{info.get('formula')}`")
                    st.caption(f"_{info.get('interpretation', '')}_")
                else:
                    missing_str = ", ".join(info.get("missing", []))
                    st.metric(label=ratio_name, value="Inputs Incomplete")
                    st.caption(f"Missing required disclosure: `{missing_str}`")
            col_idx += 1
