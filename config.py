import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# NVIDIA Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").strip()
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3.5-super-vl-120b-a12b").strip()

# Tavily Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Database Configuration
DATABASE_PATH = BASE_DIR / "financial_butterfly.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH.as_posix()}")

# App Secret Key for session / security
SECRET_KEY = os.getenv("SECRET_KEY", "financial_butterfly_effect_default_secret_2026")

# SEC EDGAR User-Agent header (required by SEC EDGAR API guidelines)
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "FinancialButterflyEffect StudentResearch/1.0 (academic.research@university.edu)")

# Data Availability Constants
STATUS_FOUND = "PUBLIC INFORMATION FOUND"
STATUS_NOT_AVAILABLE = "NOT PUBLICLY AVAILABLE"
STATUS_RESTRICTED = "INFORMATION IS PRIVATE / ACCESS RESTRICTED"
