# 🦋 The Financial Butterfly Effect

**AI-Based Multi-Organisation Financial Ripple-Effect Analysis & Decision Support System**

---

## 🏛️ Executive Summary

**The Financial Butterfly Effect** is an enterprise-grade financial intelligence and decision-support platform designed for corporate boards, CFOs, financial managers, and analysts. The central thesis of the platform is that **micro-financial decisions made today create cascading, interconnected first- and second-order consequences over multi-year horizons**.

For example, when an enterprise executes an operating expenditure (OPEX) reduction of 2%:
1. **Direct Impact (Period 0):** Operating expenses decrease; immediate operating margin widens.
2. **First-Order Ripple (T+1):** Liquid cash reserves accumulate; debt leverage ratios decline.
3. **Second-Order Repercussion (T+2 to T+3):** Reinvesting retained capital into modern R&D elevates employee productivity and throughput.
4. **Critical Negative Feedback Warning:** Conversely, if cost reductions fall disproportionately on salaries, training, and maintenance, workforce morale and equipment reliability deteriorate, triggering an unbudgeted contraction in delivery capacity and top-line sales.

The platform provides a **mathematical, non-linear ripple engine** to forecast these multidimensional trade-offs, preventing myopic financial planning.

---

## 🛠️ Technology Stack

| Domain | Technology / Library |
| :--- | :--- |
| **Frontend UI** | Streamlit, Bespoke Deep Navy / Emerald / Gold Custom CSS |
| **Interactive Visualisation** | Plotly Graph Objects, Express, Subplots |
| **Backend & Language** | Python 3.11+ |
| **Artificial Intelligence** | NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`), NVIDIA Nemotron Models, OpenAI-Compatible Python SDK |
| **Machine Learning** | Scikit-learn (Linear Regression, Random Forest Regressors, Isolation Forest) |
| **Mathematical Simulation** | NetworkX (Directed Graph Dependency Modeling), NumPy, SciPy |
| **Data Processing** | Pandas |
| **Database & ORM** | SQLAlchemy 2.0, SQLite (default) / PostgreSQL-compatible architecture |
| **PDF Dossiers** | ReportLab (Vector styling, tables, flowables) |
| **Security & Auth** | Bcrypt cryptographic hashing, Role-Based Access Control (RBAC) |
| **Testing** | Pytest (19 automated unit & isolation tests) |

---

## 📂 Project Directory Structure

```
Financial_Butterfly_Effect/
│
├── app.py                          # Master Streamlit Application & Router
├── config.py                       # System configurations & environment loader
├── requirements.txt                # Production Python dependencies
├── conftest.py                     # Pytest environment bootstrap
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── README.md                       # Comprehensive system documentation
│
├── database/                       # Database layer
│   ├── connection.py               # Engine, thread-safe sessionmakers
│   ├── models.py                   # SQLAlchemy 2.0 ORM models (12 tables)
│   └── initialisation.py           # Database initialisation & synthetic demo seeder
│
├── modules/                        # Backend business logic & engines
│   ├── authentication.py           # Bcrypt hashing & RBAC permission checks
│   ├── organisation.py             # Tenant creation, memberships, isolation
│   ├── financial_data.py           # Ledger entries, CSV parser, calculated metrics
│   ├── investment.py               # Portfolio allocation, simple/compound interest, NPV
│   ├── savings.py                  # Expense optimization & reinvestment compounding
│   ├── butterfly_engine.py         # NetworkX ripple matrix engine (delta_next = A @ delta)
│   ├── ai_prediction.py            # ML forecasting (LR, RF) & Isolation Forest
│   ├── risk_analysis.py            # Solvency scoring, Monte Carlo 1,000 runs, sensitivity
│   ├── nvidia_client.py            # Dedicated NVIDIA NIM Nemotron client & fallback
│   ├── ai_assistant.py             # Organisation-aware financial copilot
│   ├── financial_analysis.py       # Balance sheet health scoring (0-100)
│   └── reports.py                  # ReportLab executive PDF dossier generator
│
├── pages/                          # Streamlit UI page views
│   ├── dashboard.py                # Executive KPI overview & health meters
│   ├── simulator.py                # The Interactive Butterfly Effect Simulator
│   ├── financial_records.py        # Ledger table, manual entry, CSV bulk import
│   ├── investments.py              # Portfolio analysis, asset registration, NPV
│   ├── savings.py                  # Departmental expense cuts & reinvestment simulator
│   ├── scenarios.py                # Macro and custom scenario comparison
│   ├── predictions.py              # ML forward forecasting & transaction anomaly detection
│   ├── risk_analysis.py            # Multi-dimensional risk radar, Monte Carlo, sensitivity
│   ├── ai_assistant.py             # Conversational copilot with quick queries
│   ├── organisations.py            # Entity switcher, departments, role assignments
│   ├── reports.py                  # Board PDF compilation & instant download
│   └── settings.py                 # System diagnostics, NVIDIA NIM health check
│
├── utils/                          # Cross-cutting utility helpers
│   ├── calculations.py             # Financial math (NPV, ROI, ratios, INR formatting)
│   ├── validation.py               # Email, numeric, and CSV schema validators
│   └── visualisations.py           # Deep Navy/Emerald/Gold Plotly charts
│
├── data/
│   └── sample_financial_data.csv   # Sample CSV template for upload testing
│
├── tests/                          # Automated Pytest suite
│   ├── test_authentication.py
│   ├── test_financial_calculations.py
│   ├── test_butterfly_engine.py
│   ├── test_organisation_isolation.py
│   ├── test_nvidia_client.py
│   └── test_risk_analysis.py
│
├── models/                         # Serialized ML model storage
└── reports/                        # Compiled PDF dossiers
```

---

## 🚀 Installation & Launch Instructions

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- Git (optional).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy the `.env.example` file to create your local `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure your credentials:
```env
# Optional: NVIDIA NIM API credentials (from https://build.nvidia.com/)
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-4-340b-instruct
NVIDIA_TIMEOUT_SECONDS=30

# Database URL (SQLite default, or PostgreSQL)
DATABASE_URL=sqlite:///./financial_butterfly.db

# Localization
DEFAULT_CURRENCY=₹
CURRENCY_CODE=INR
```
> **Offline Fallback Guarantee:** If an external NVIDIA API key is unavailable or the endpoint is unreachable, the system automatically transitions into an **autonomous, deterministic financial expert mode**. The entire application remains 100% operational without crashing.

### 4. Initialize Database & Seed Demonstration Data
```bash
python -m database.initialisation
```
This sets up all SQLite tables and seeds 3 realistic synthetic organisations with 12 quarters of historical records.

### 5. Launch the Streamlit Application
```bash
streamlit run app.py
```
The application will launch in your default browser at `http://localhost:8501`.

---

## 🔑 Demonstration Credentials

| Persona | Username | Password | Role | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Executive Administrator** | `admin` | `admin123` | Platform Administrator | Universal access across all organisations, user assignment, system settings. |
| **Lead Financial Analyst** | `analyst` | `analyst123` | Financial Analyst | View dashboards, run simulations, query AI assistant, export reports. |

*Quick 1-click test login buttons are also integrated directly into the login screen.*

---

## 🏢 Pre-Configured Synthetic Organisations

The platform comes pre-seeded with 3 synthetic organisations:

1. **ABC Manufacturing Ltd.**
   - **Sector:** Precision Industrial & Automotive Machinery
   - **Annual Operating Budget:** ₹10.00 Crore (₹100,000,000)
   - **Profile:** High asset base, capital-intensive manufacturing, 12 quarters of production records, robotic CNC investments.
2. **XYZ Investment Group**
   - **Sector:** Boutique Private Equity & Asset Management
   - **Investment Capital:** ₹5.00 Crore (₹50,000,000)
   - **Profile:** Asset-light, high-yield securities, private equity placements, low debt.
3. **Future Education Trust**
   - **Sector:** Educational Foundation & STEM Academy
   - **Annual Operating Budget:** ₹2.00 Crore (₹20,000,000)
   - **Profile:** Endowment funds, student scholarships, grants, low operating leverage.

*All demonstration data is explicitly labeled as synthetic.*

---

## 🧮 Mathematical Model: The Butterfly Engine

The heart of the application is the **Butterfly Engine** (`modules/butterfly_engine.py`), which models corporate financial transmission using a directed, weighted dependency network of 12 core nodes:
- Revenue
- Operating Expenses
- Cash Reserves
- Investment Capital
- Employee Productivity
- Production Capacity
- Research and Development
- Marketing
- Profitability
- Liquidity
- Debt
- Organisational Growth

### Mathematical State Equation
$$\Delta_{t+1} = \gamma \cdot \tanh(A \cdot \Delta_t) + \mathbf{f}_{\text{feedback}}(\Delta_t)$$

Where:
- $\Delta_t \in \mathbb{R}^{12}$ is the percentage delta state vector at period $t$.
- $A \in \mathbb{R}^{12 \times 12}$ is the weighted causal sensitivity matrix.
- $\gamma \approx 0.85$ is the decay/damping factor preventing runaway oscillations.
- $\tanh(\cdot)$ guarantees bounded saturation within realistic economic bounds.
- $\mathbf{f}_{\text{feedback}}$ is the non-linear operational hazard function: when operating expenses are cut by more than $10\%$, employee productivity experiences a severe negative drag penalty, capturing burnout, staff attrition, and equipment degradation.

---

## 🧪 Automated Test Suite

Run all unit and integration tests using Pytest:
```bash
python -m pytest tests -v
```

### Test Coverage Highlights:
- `test_authentication.py`: Bcrypt hashing, authentication success/failure, role hierarchy validation.
- `test_financial_calculations.py`: Operating profit, net profit, margins, current ratio, debt ratio, simple/compound interest, NPV, Indian currency formatting.
- `test_butterfly_engine.py`: NetworkX graph verification, ripple propagation, damping factor, numerical stability, negative penalty execution.
- `test_organisation_isolation.py`: Cross-tenant database isolation, multi-tenant membership checks.
- `test_nvidia_client.py`: Client initialization, availability probing, deterministic offline expert fallback, ripple explanation synthesis.
- `test_risk_analysis.py`: Multi-dimensional risk score, 1,000-run Monte Carlo simulation, VaR 95%, two-way sensitivity matrix.

---

## ⚖️ Assumptions & Limitations

1. **Analytical Projections:** All investment yields, forecast trajectories, and ripple effects represent mathematical simulations based on user assumptions and historical correlations. They do not constitute commercial guarantees.
2. **Synthetic Data:** Default data pre-seeded in the database is synthetic and intended for stress-testing and demonstration.
3. **Audit Compliance:** Formal financial decisions should be verified by certified financial advisors and statutory auditors.

---

## 📄 License
Enterprise Decision Support Architecture © 2026. Built with Python, Streamlit, and NVIDIA NIM AI.
