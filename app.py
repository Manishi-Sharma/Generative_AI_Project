import sys
from pathlib import Path

# Ensure root workspace directory is in python search path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from config import SECRET_KEY
from database.connection import init_db
from auth.authentication import authenticate_user, create_user
from views.organisation_search import render_organisation_search
from views.financial_overview import render_financial_overview
from views.butterfly_analysis import render_butterfly_analysis
from views.ai_reports import render_ai_reports
from modules.organisation_search import OrganisationSearchEngine
from modules.public_data_collector import PublicDataCollector
from modules.financial_calculations import FinancialCalculator

# 1. Page Configuration
st.set_page_config(
    page_title="The Financial Butterfly Effect",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Database tables
init_db()

# 3. Custom CSS for Modern Dark Navy FinTech Interface
DARK_NAVY_CSS = """
<style>
    /* Global Base */
    .stApp {
        background-color: #0A1128 !important;
        color: #FEFCFB !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: #0A1128 !important;
    }

    /* Hide Deploy Button and Header Clutter */
    .stDeployButton,
    div[data-testid="stToolbarActions"],
    div[data-testid="stDeployButton"],
    button[title="Deploy this app"],
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #001F54 !important;
        border-right: 1px solid #034078 !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #FEFCFB !important;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #001F54 !important;
        padding: 14px !important;
        border-radius: 8px !important;
        border: 1px solid #1282A2 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: #A0C4E2 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #FEFCFB !important;
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    /* Inputs and Buttons */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #001F54 !important;
        color: #FEFCFB !important;
        border: 1px solid #1282A2 !important;
        border-radius: 6px !important;
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, #1282A2 0%, #034078 100%) !important;
        color: #FEFCFB !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    button[kind="secondary"] {
        background-color: #001F54 !important;
        color: #00F5D4 !important;
        border: 1px solid #1282A2 !important;
        border-radius: 6px !important;
    }

    /* Dataframe and Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1282A2 !important;
        border-radius: 8px !important;
    }

    /* Info & Alert Callouts */
    .stAlert {
        background-color: #001F54 !important;
        color: #FEFCFB !important;
        border: 1px solid #1282A2 !important;
    }

    /* Custom Title Pill */
    .title-pill {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(18, 130, 162, 0.2);
        border: 1px solid #1282A2;
        border-radius: 20px;
        color: #00F5D4;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
</style>
"""
st.markdown(DARK_NAVY_CSS, unsafe_allow_html=True)

# 4. Session State Management
if "user" not in st.session_state:
    st.session_state.user = None
if "selected_org" not in st.session_state:
    st.session_state.selected_org = None
if "financial_records" not in st.session_state:
    st.session_state.financial_records = []
if "calculations" not in st.session_state:
    st.session_state.calculations = {}
if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None
if "ai_explanation" not in st.session_state:
    st.session_state.ai_explanation = ""

# 5. FIRST SCREEN: DIRECT AUTHENTICATION
if st.session_state.user is None:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<span class='title-pill'>FINANCIAL INTELLIGENCE SYSTEM</span>", unsafe_allow_html=True)
        st.markdown("# 🦋 The Financial Butterfly Effect")
        st.markdown("Please authenticate to access the corporate financial analysis and ripple-effect engine.")

        auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])

        with auth_tab1:
            st.markdown("### Sign In to Your Account")
            login_email = st.text_input("Email Address", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_password")
            login_btn = st.button("Sign In", type="primary", use_container_width=True)

            if login_btn:
                success, msg, user_obj = authenticate_user(login_email, login_pass)
                if success:
                    st.session_state.user = user_obj
                    st.success("Authenticated successfully!")
                    st.rerun()
                else:
                    st.error(msg)

        with auth_tab2:
            st.markdown("### Create New Account")
            reg_name = st.text_input("Full Name (Optional)", key="reg_name")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_pass = st.text_input("Password (min. 6 characters)", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            reg_btn = st.button("Create Account", type="primary", use_container_width=True)

            if reg_btn:
                if reg_pass != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, msg, user_obj = create_user(reg_email, reg_pass, reg_name)
                    if success:
                        st.session_state.user = user_obj
                        st.success("Account created! Logging you in...")
                        st.rerun()
                    else:
                        st.error(msg)

    st.stop()

# 6. AUTHENTICATED USER DASHBOARD
# Sidebar Navigation
with st.sidebar:
    st.markdown("<span class='title-pill'>THE FINANCIAL BUTTERFLY EFFECT</span>", unsafe_allow_html=True)

    # Active Organisation Status Display
    if st.session_state.selected_org:
        org_name = st.session_state.selected_org.get("name")
        ticker = st.session_state.selected_org.get("ticker")
        ticker_str = f" ({ticker})" if ticker else ""
        st.markdown(f"""
        <div style="background-color: #0A1128; padding: 10px 14px; border-radius: 6px; border: 1px solid #00F5D4; margin: 10px 0;">
            <span style="color: #00F5D4; font-size: 11px; font-weight: bold;">ACTIVE ORGANISATION:</span><br/>
            <span style="color: #FEFCFB; font-weight: 700; font-size: 14px;">{org_name}{ticker_str}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #0A1128; padding: 10px 14px; border-radius: 6px; border: 1px dashed #1282A2; margin: 10px 0;">
            <span style="color: #A0C4E2; font-size: 12px;">No Organisation Selected</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    menu_selection = st.radio(
        "Go to:",
        [
            "1. Organisation Search",
            "2. Financial Overview",
            "3. Butterfly Effect Analysis",
            "4. AI Insights & Reports"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    # Account & Logout Controls
    if st.session_state.user:
        st.markdown(f"**Signed in as:**")
        st.caption(f"{st.session_state.user.email}")
        if getattr(st.session_state.user, "full_name", None):
            st.caption(f"_{st.session_state.user.full_name}_")

    if st.button("Log Out", type="secondary", use_container_width=True):
        st.session_state.user = None
        st.session_state.selected_org = None
        st.session_state.financial_records = []
        st.session_state.calculations = {}
        st.session_state.simulation_result = None
        st.session_state.ai_explanation = ""
        st.rerun()

# Top persistent organisation banner in main area
if st.session_state.selected_org:
    active_name = st.session_state.selected_org.get("name")
    active_country = st.session_state.selected_org.get("country", "Global")
    active_industry = st.session_state.selected_org.get("industry", "Enterprise")
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #001F54 0%, #034078 100%); padding: 10px 20px; border-radius: 8px; border-left: 4px solid #00F5D4; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="color: #00F5D4; font-size: 11px; font-weight: bold; text-transform: uppercase;">Currently Analyzing</span>
            <h3 style="margin: 0; color: #FEFCFB; font-size: 18px;">{active_name}</h3>
        </div>
        <div style="text-align: right; color: #A0C4E2; font-size: 12px;">
            <b>Jurisdiction:</b> {active_country} | <b>Industry:</b> {active_industry}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 7. Route to Active Screen
if menu_selection == "1. Organisation Search":
    render_organisation_search()
elif menu_selection == "2. Financial Overview":
    render_financial_overview()
elif menu_selection == "3. Butterfly Effect Analysis":
    render_butterfly_analysis()
elif menu_selection == "4. AI Insights & Reports":
    render_ai_reports()
