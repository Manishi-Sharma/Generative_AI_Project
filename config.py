"""
Configuration management for The Financial Butterfly Effect application.
Loads settings from environment variables and sets system-wide constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# App Info
APP_NAME = "The Financial Butterfly Effect"
APP_SUBTITLE = "AI-Based Multi-Organisation Financial Ripple-Effect Analysis & Decision Support System"
APP_VERSION = "2.0.0"

# Security & Sessions
SECRET_KEY = os.getenv("SECRET_KEY", "financial-butterfly-secret-key-change-in-production-2026")

# Database Configuration (SQLite default with full PostgreSQL compatibility)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'financial_butterfly.db'}")

# NVIDIA NIM AI Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
# Primary Nemotron reasoning/instruction model with fast fallback options
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-4-340b-instruct")
NVIDIA_TIMEOUT_SECONDS = int(os.getenv("NVIDIA_TIMEOUT_SECONDS", "30"))

# Currency and Localization
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "₹")
CURRENCY_CODE = os.getenv("CURRENCY_CODE", "INR")

# System Directories
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

for directory in [REPORTS_DIR, MODELS_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Butterfly Engine Configuration
DEFAULT_DAMPING_FACTOR = 0.85  # Exponential decay to ensure stability
MAX_SIMULATION_YEARS = 5
DEFAULT_MONTE_CARLO_ITERATIONS = 1000

# Roles definition
ROLE_PLATFORM_ADMIN = "platform_admin"
ROLE_ORG_ADMIN = "org_admin"
ROLE_FINANCIAL_MANAGER = "financial_manager"
ROLE_FINANCIAL_ANALYST = "financial_analyst"

ALL_ROLES = [
    ROLE_PLATFORM_ADMIN,
    ROLE_ORG_ADMIN,
    ROLE_FINANCIAL_MANAGER,
    ROLE_FINANCIAL_ANALYST,
]

ROLE_DISPLAY_NAMES = {
    ROLE_PLATFORM_ADMIN: "Platform Administrator",
    ROLE_ORG_ADMIN: "Organisation Administrator",
    ROLE_FINANCIAL_MANAGER: "Financial Manager",
    ROLE_FINANCIAL_ANALYST: "Financial Analyst",
}
