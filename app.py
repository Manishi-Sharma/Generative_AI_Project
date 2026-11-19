"""
THE FINANCIAL BUTTERFLY EFFECT
AI-Based Multi-Organisation Financial Ripple-Effect Analysis & Decision Support System
Master Streamlit Application
"""

import streamlit as st
import config
from database.connection import init_db, get_db_context
from database.initialisation import seed_database
from database.models import User, Organisation
from modules.authentication import (
    authenticate_user,
    register_user,
    check_permission,
)
from modules.organisation import get_user_organisations, get_organisation_by_id
from modules.nvidia_client import nvidia_client

# Modular Page Renderers
from pages.dashboard import render_dashboard
from pages.organisations import render_organisations_page
from pages.financial_records import render_financial_records_page
from pages.investments import render_investments_page
from pages.savings import render_savings_page
from pages.simulator import render_simulator_page
from pages.scenarios import render_scenarios_page
from pages.predictions import render_predictions_page
from pages.risk_analysis import render_risk_analysis_page
from pages.ai_assistant import render_ai_assistant_page
from pages.reports import render_reports_page
from pages.settings import render_settings_page


# Streamlit Page Setup
try:
    st.set_page_config(
        page_title=config.APP_NAME,
        page_icon="🦋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
except Exception:
    pass

# Custom Enterprise CSS (Deep Navy, Emerald Green, Subtle Gold)
CUSTOM_CSS = """
<style>
    /* Global Background and Typography */
    .stApp {
        background: linear-gradient(135deg, #070d1e 0%, #0b132b 50%, #0d1b2a 100%);
        color: #e2e8f0;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Top Header and Branding */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0c1427 !important;
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] .stMarkdown h1, 
    section[data-testid="stSidebar"] .stMarkdown h2, 
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #f59e0b !important;
    }

    /* Card Containers */
    div[data-testid="stMetric"] {
        background-color: #1c2541 !important;
        border: 1px solid #273549 !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] {
        font-weight: 600 !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 20px !important;
        transition: all 0.2s ease-in-out;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(90deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    button[kind="secondary"] {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    button[aria-selected="true"] {
        color: #10b981 !important;
        border-bottom-color: #10b981 !important;
    }

    /* Form Inputs */
    input, select, textarea {
        background-color: #131d36 !important;
        color: #f8fafc !important;
        border: 1px solid #273549 !important;
        border-radius: 6px !important;
    }

    /* Dataframe styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #273549;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: #132238 !important;
        border: 1px solid #224263 !important;
        border-radius: 8px !important;
    }
</style>
"""
try:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
except Exception:
    pass


def init_app_state() -> None:
    """Ensure database is seeded and session state is initialized."""
    if "db_initialized" not in st.session_state:
        seed_database()
        st.session_state["db_initialized"] = True

    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "current_org_id" not in st.session_state:
        st.session_state["current_org_id"] = None


def render_login_registration() -> None:
    """Renders authentication portal when user is not signed in."""
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_a, col_main, col_b = st.columns([1, 1.8, 1])
    with col_main:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-size: 50px;">🦋</div>
            <div style="font-size: 26px; font-weight: 800; color: #f59e0b; letter-spacing: 1px; margin-top: 8px;">
                {config.APP_NAME.upper()}
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                {config.APP_SUBTITLE}
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register, tab_quick = st.tabs(["🔐 Sign In", "📝 Create Account", "⚡ Demo Access"])

        with tab_login:
            with st.form("login_form"):
                uname = st.text_input("Username or Email", value="admin")
                pwd = st.text_input("Password", type="password", value="admin123")
                submit_login = st.form_submit_button("Sign In to Decision Suite", type="primary", use_container_width=True)

                if submit_login:
                    with get_db_context() as db:
                        success, user, msg = authenticate_user(db, uname, pwd)
                        if success:
                            st.session_state["user"] = user
                            st.success(f"Welcome back, {user.full_name}!")
                            st.rerun()
                        else:
                            st.error(msg)

        with tab_register:
            with st.form("reg_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Dr. Rajesh Sharma")
                reg_uname = st.text_input("Username", placeholder="e.g. rsharma")
                reg_email = st.text_input("Corporate Email", placeholder="e.g. rsharma@company.com")
                reg_pwd = st.text_input("Password (min 6 characters)", type="password")
                reg_role = st.selectbox("Designation", [
                    config.ROLE_FINANCIAL_ANALYST,
                    config.ROLE_FINANCIAL_MANAGER,
                    config.ROLE_ORG_ADMIN,
                ], format_func=lambda x: config.ROLE_DISPLAY_NAMES.get(x, x))
                submit_reg = st.form_submit_button("Register Account", type="primary", use_container_width=True)

                if submit_reg:
                    if len(reg_pwd) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif not reg_uname or not reg_email or not reg_name:
                        st.error("All fields are required.")
                    else:
                        with get_db_context() as db:
                            success, new_user, msg = register_user(
                                db,
                                username=reg_uname,
                                email=reg_email,
                                password=reg_pwd,
                                full_name=reg_name,
                                role=reg_role,
                            )
                            if success:
                                st.session_state["user"] = new_user
                                st.success("Account registered successfully!")
                                st.rerun()
                            else:
                                st.error(msg)

        with tab_quick:
            st.markdown("#### Quick Demonstration Credentials")
            st.write("Click any persona below for instant 1-click test authentication:")
            c_adm, c_ana = st.columns(2)
            with c_adm:
                if st.button("👑 Admin Persona (Universal Access)", use_container_width=True):
                    with get_db_context() as db:
                        _, user, _ = authenticate_user(db, "admin", "admin123")
                        st.session_state["user"] = user
                        st.rerun()
            with c_ana:
                if st.button("📊 Analyst Persona (Standard Access)", use_container_width=True):
                    with get_db_context() as db:
                        _, user, _ = authenticate_user(db, "analyst", "analyst123")
                        st.session_state["user"] = user
                        st.rerun()


def main():
    init_app_state()

    current_user = st.session_state["user"]
    if not current_user:
        render_login_registration()
        return

    # Authenticated Session
    with get_db_context() as db:
        user_orgs = get_user_organisations(db, current_user)

    if not user_orgs:
        st.error("You are not currently assigned to any organisations. Contact a Platform Administrator.")
        if st.sidebar.button("Sign Out"):
            st.session_state["user"] = None
            st.rerun()
        return

    # Ensure valid current_org_id
    if not st.session_state["current_org_id"] or st.session_state["current_org_id"] not in [o.id for o in user_orgs]:
        st.session_state["current_org_id"] = user_orgs[0].id

    with get_db_context() as db:
        current_org = get_organisation_by_id(db, st.session_state["current_org_id"])

    # -----------------------------
    # Sidebar Navigation & Branding
    # -----------------------------
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1e293b;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 28px;">🦋</span>
                <div>
                    <div style="font-size: 15px; font-weight: 800; color: #f59e0b; line-height: 1.1;">FINANCIAL BUTTERFLY</div>
                    <div style="font-size: 10px; color: #94a3b8; font-weight: 600;">EFFECT & DECISION SYSTEM</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Active Organisation Switcher Pill
        org_names = {o.id: o.name for o in user_orgs}
        selected_org_id = st.selectbox(
            "🏢 Active Organisation",
            options=list(org_names.keys()),
            format_func=lambda x: org_names[x],
            index=list(org_names.keys()).index(current_org.id) if current_org.id in org_names else 0,
        )
        if selected_org_id != current_org.id:
            st.session_state["current_org_id"] = selected_org_id
            st.rerun()

        st.markdown("---")

        # Navigation Menu
        nav_selection = st.radio(
            "Navigation",
            options=[
                "🏛️ Executive Dashboard",
                "🦋 Butterfly Effect Simulator",
                "📊 Financial Data Management",
                "📈 Investment Portfolio",
                "💰 Savings Optimisation",
                "⚖️ Scenario Comparison",
                "🔮 Financial Forecasting (ML)",
                "🛡️ Risk Engine & Stress Testing",
                "🤖 AI Financial Assistant",
                "🏢 Organisation Management",
                "📑 Reports & PDF Export",
                "⚙️ System Settings",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")

        # NVIDIA NIM Status Pill
        is_nim, _ = nvidia_client.is_available()
        nim_badge = "🟢 NIM Active" if is_nim else "⚡ Fallback Mode"
        st.markdown(f"""
        <div style="background-color: #131d36; border: 1px solid #273549; border-radius: 8px; padding: 10px; font-size: 11px;">
            <div style="color: #94a3b8;">NVIDIA Nemotron: <b style="color: {'#10b981' if is_nim else '#f59e0b'};">{nim_badge}</b></div>
            <div style="color: #64748b; margin-top: 2px;">Currency: <b>{current_org.currency} ({config.CURRENCY_CODE})</b></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(" ")

        # User Profile & Logout
        col_u1, col_u2 = st.columns([1.8, 1])
        with col_u1:
            st.markdown(f"**{current_user.full_name}**<br><span style='font-size:11px; color:#94a3b8;'>{config.ROLE_DISPLAY_NAMES.get(current_user.role, current_user.role)}</span>", unsafe_allow_html=True)
        with col_u2:
            if st.button("Sign Out", type="secondary"):
                st.session_state["user"] = None
                st.session_state["current_org_id"] = None
                st.rerun()

    # -----------------------------
    # Main Page Router
    # -----------------------------
    if "Executive Dashboard" in nav_selection:
        render_dashboard(current_org, current_user)
    elif "Butterfly Effect Simulator" in nav_selection:
        render_simulator_page(current_user, current_org)
    elif "Financial Data" in nav_selection:
        render_financial_records_page(current_user, current_org)
    elif "Investment Portfolio" in nav_selection:
        render_investments_page(current_user, current_org)
    elif "Savings Optimisation" in nav_selection:
        render_savings_page(current_user, current_org)
    elif "Scenario Comparison" in nav_selection:
        render_scenarios_page(current_user, current_org)
    elif "Financial Forecasting" in nav_selection:
        render_predictions_page(current_user, current_org)
    elif "Risk Engine" in nav_selection:
        render_risk_analysis_page(current_user, current_org)
    elif "AI Financial Assistant" in nav_selection:
        render_ai_assistant_page(current_user, current_org)
    elif "Organisation Management" in nav_selection:
        render_organisations_page(current_user, current_org)
    elif "Reports" in nav_selection:
        render_reports_page(current_user, current_org)
    elif "System Settings" in nav_selection:
        render_settings_page(current_user, current_org)


if __name__ == "__main__":
    main()
