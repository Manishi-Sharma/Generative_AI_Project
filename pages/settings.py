"""
Page: System Settings & Platform Administration
Manages environment configurations, NVIDIA NIM endpoint diagnostics,
database statistics, and user account profiles.
"""

from typing import Any
import streamlit as st
from database.connection import get_db_context
from database.models import User, Organisation, FinancialRecord, Investment
from modules.nvidia_client import nvidia_client
from modules.authentication import check_permission
import config


def render_settings_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## ⚙️ Platform Settings & Diagnostics")

    tab_ai, tab_db, tab_user = st.tabs([
        "🤖 NVIDIA NIM AI Configuration",
        "🗄️ Database & Environment Health",
        "👤 Account & Security Profile"
    ])

    with tab_ai:
        st.markdown("### NVIDIA NIM API Integration Status")
        is_avail, msg = nvidia_client.is_available()

        if is_avail:
            st.success(f"🟢 **Connected:** {msg}")
        else:
            st.warning(f"⚡ **Offline Fallback Mode:** {msg}")

        st.markdown("#### Active Configuration")
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Base URL:** `{config.NVIDIA_BASE_URL}`")
            st.write(f"**Default Model:** `{config.NVIDIA_MODEL}`")
            st.write(f"**Timeout:** `{config.NVIDIA_TIMEOUT_SECONDS}s`")
        with c2:
            key_preview = f"{config.NVIDIA_API_KEY[:7]}...{config.NVIDIA_API_KEY[-4:]}" if len(config.NVIDIA_API_KEY) > 12 else "Not Set (Fallback)"
            st.write(f"**API Key:** `{key_preview}`")
            st.write(f"**SDK Protocol:** `OpenAI-Compatible Client`")

        if st.button("Test NVIDIA NIM Connection"):
            with st.spinner("Pinging NVIDIA NIM API endpoint..."):
                test_avail, test_msg = nvidia_client.is_available()
                if test_avail:
                    st.success(test_msg)
                else:
                    st.info(f"Test Result: {test_msg}")

    with tab_db:
        st.markdown("### Database Diagnostics")
        with get_db_context() as db:
            org_count = db.query(Organisation).count()
            user_count = db.query(User).count()
            record_count = db.query(FinancialRecord).count()
            inv_count = db.query(Investment).count()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Organisations", org_count)
        with c2:
            st.metric("Active Users", user_count)
        with c3:
            st.metric("Financial Ledger Records", record_count)
        with c4:
            st.metric("Investment Positions", inv_count)

        st.write(f"**Database Engine:** `SQLite / SQLAlchemy ORM (PostgreSQL Ready)`")
        st.write(f"**Default Currency:** `{config.DEFAULT_CURRENCY}` ({config.CURRENCY_CODE})")

    with tab_user:
        st.markdown("### User Profile & Access Control")
        st.write(f"**Full Name:** {current_user.full_name}")
        st.write(f"**Username:** `@{current_user.username}`")
        st.write(f"**Email:** {current_user.email}")
        st.write(f"**Assigned Global Role:** `{config.ROLE_DISPLAY_NAMES.get(current_user.role, current_user.role)}`")
        st.write(f"**Account Status:** {'Active' if current_user.is_active else 'Disabled'}")
