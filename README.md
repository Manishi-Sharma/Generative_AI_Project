# The Financial Butterfly Effect
### AI-Powered Public Financial Analysis and Ripple-Effect Prediction System

**The Financial Butterfly Effect** is an academic mini-project designed to demonstrate how a single, seemingly minor corporate financial decision (e.g., reducing operating expenses by 5% or raising CapEx by 10%) cascades into multiple direct, indirect, and higher-order ripple effects across an organisation's entire financial ecosystem.

---

## 1. Project Overview

The application empowers students, researchers, and financial analysts to:
1. **Authenticate Securely:** Register and sign in with bcrypt password hashing and session management.
2. **Discover Any Organisation:** Search public registries and web sources for any real business (unrestricted to any predefined company list).
3. **Retrieve Public Financial Disclosures:** Ingest verified figures from U.S. SEC EDGAR XBRL filings, public balance sheets, and investor relations documents.
4. **Track Data Availability Transparently:** Explicitly mark metrics with:
   - `PUBLIC INFORMATION FOUND` (green)
   - `NOT PUBLICLY AVAILABLE` (amber)
   - `INFORMATION IS PRIVATE / ACCESS RESTRICTED` (red)
5. **Compute Deterministic Financial Ratios:** Calculate operational margins, return on equity (ROE), return on assets (ROA), and liquidity metrics using pure Python formulas without converting missing data to zero.
6. **Simulate the Butterfly Effect:** Propagate hypothetical financial shocks across a 10-node corporate dependency network using a stabilized matrix multiplication model with dampening:
   $$\Delta X^{(t+1)} = \lambda \cdot (W @ \Delta X^{(t)})$$
7. **Generate NVIDIA Nemotron AI Insights:** Interpret the ripple effects, distinguish verified facts from simulation assumptions, and balance positive opportunities against systemic risks.
8. **Export Audit Reports:** Download a structured, publication-ready PDF report compiled via ReportLab.

---

## 2. Technology Stack

- **Python:** 3.11+
- **Frontend / UI:** Streamlit (custom dark navy fintech UI)
- **AI Interpretation:** NVIDIA Nemotron (`nvidia/nemotron-3.5-super-vl-120b-a12b` via NVIDIA NIM API)
- **Public Search:** Tavily Search API & U.S. SEC EDGAR REST API
- **Graph & Mathematical Modeling:** NetworkX & NumPy
- **Interactive Visualizations:** Plotly (directed dependency networks & scenario comparisons)
- **Data Engineering:** Pandas, Requests, BeautifulSoup, PyMuPDF (`fitz`)
- **Database & Security:** SQLite, SQLAlchemy, bcrypt
- **Reporting:** ReportLab (vector PDF generation)

---

## 3. Installation Instructions

### Prerequisites
- Python 3.11 or higher
- Git

### Step 1: Clone or Navigate to the Repository
```bash
cd "c:\Users\HP\Desktop\Financial Butterly Effect"
```

### Step 2: Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 4. API Key Configuration

Create a `.env` file in the root directory (refer to `.env.example`):

```bash
# Copy template
copy .env.example .env
```

Edit `.env` to configure your API keys:

```env
# NVIDIA NIM API for Nemotron 120B
NVIDIA_API_KEY=nvapi-your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=nvidia/nemotron-3.5-super-vl-120b-a12b

# Tavily Search API for Public Web Discovery (Optional but Recommended)
TAVILY_API_KEY=tvly-your_tavily_api_key_here

# SQLite Database Location
DATABASE_URL=sqlite:///./financial_butterfly.db
```

> **Note on Graceful Fallback:** If `NVIDIA_API_KEY` or `TAVILY_API_KEY` are not set, the application continues to function cleanly using official public SEC EDGAR disclosures and a deterministic analytical interpretation engine.

---

## 5. NVIDIA Model Information

- **Model Identifier:** `nvidia/nemotron-3.5-super-vl-120b-a12b`
- **Provider:** NVIDIA NIM API (`https://integrate.api.nvidia.com/v1`)
- **Role in System:**
  - Explains the economic rationale behind first-order and second-order ripple effects.
  - Highlights sensitivity to cost friction, tax leakages, and debt servicing.
  - Distinguishes strictly between verified public disclosures and simulation assumptions.
  - **Does NOT invent or calculate numbers:** all numerical operations are performed deterministically by Python and NumPy.

---

## 6. Public Data Sources

1. **U.S. SEC EDGAR API:**
   - Free, official, public endpoint for company tickers and XBRL `companyfacts` JSON.
   - Extracts standardized US-GAAP metrics: Revenues, Operating Income/Loss, Net Income/Loss, Total Assets, Liabilities, Stockholders' Equity, Long-Term Debt, Operating Cash Flow, and CapEx.
   - Requires an SEC-compliant User-Agent header (included).
2. **Tavily Search API:**
   - Performs advanced web discovery across corporate investor relations portals, annual PDF reports, and press releases.
3. **Public Corporate Knowledgebases:**
   - Wikipedia / Registry API fallback for general corporate descriptions and disambiguation.

---

## 7. Working Methodology & Pipeline

```text
[User Search Query] ───> [SEC EDGAR & Tavily Discovery]
                                    │
                                    ▼
                          [Entity Disambiguation]
                                    │
                                    ▼
                         [Public Data Collector]
                       /            │           \
             [SEC XBRL]     [Web Disclosures]   [PDF Reports]
                       \            │           /
                                    ▼
                         [Data Verification Engine]
                        (Deduplication & Sanity Audit)
                                    │
                                    ▼
                      [Availability Status Assignment]
           - PUBLIC INFORMATION FOUND
           - NOT PUBLICLY AVAILABLE
           - INFORMATION IS PRIVATE / ACCESS RESTRICTED
                                    │
                                    ▼
                    [Deterministic Ratio Calculations]
                                    │
                                    ▼
                  [Butterfly Effect Simulation Engine]
                (10 Financial Nodes, Directed Graph, W Matrix)
                                    │
                                    ▼
                      [Plotly Network & Visualizations]
                                    │
                                    ▼
                    [NVIDIA Nemotron AI Interpretation]
                                    │
                                    ▼
                    [ReportLab PDF Audit Export]
```

---

## 8. Butterfly Effect Calculation Methodology

The corporate financial system is modeled as a directed dependency graph $G = (V, E)$ with 10 core financial variables:
1. `Revenue`
2. `Operating Expenses`
3. `Operating Profit`
4. `Net Profit`
5. `Cash Flow`
6. `Cash Reserves`
7. `Debt`
8. `Investment Capacity`
9. `Capital Expenditure`
10. `Business Growth`

### Dependency Propagation Formula
For iteration step $t \ge 0$:
$$\Delta X^{(0)} = [0, \dots, \delta_{\text{initial}}, \dots, 0]^T$$
$$\Delta X^{(t+1)} = \lambda \cdot (W @ \Delta X^{(t)})$$

Where:
- $W \in \mathbb{R}^{10 \times 10}$ is the weighted dependency matrix derived from corporate accounting logic.
- $\lambda \in (0, 1)$ is the **stabilization dampening coefficient** ($\lambda = 0.60$) which reflects organizational friction and prevents unbounded exponential loops.
- Cumulative percentage change:
  $$\Delta X^{\text{total}} = \sum_{t=0}^{H} \Delta X^{(t)}$$
- Where reported baseline figures $B_i$ are available:
  $$\text{Simulated}_i = B_i \times \left(1 + \frac{\Delta X_i^{\text{total}}}{100}\right)$$

---

## 9. How to Launch the Application

Run the following command in the workspace directory:

```bash
streamlit run app.py
```

Open your web browser and navigate to `http://localhost:8501`.

---

## 10. Running the Automated Test Suite

Run pytest to verify the full suite of unit and integration tests:

```bash
pytest -v
```

---

## 11. Current Limitations

1. **Unlisted / Private Companies:** Private corporations that do not publish statutory annual filings may have balance sheet indicators marked as `NOT PUBLICLY AVAILABLE` or `INFORMATION IS PRIVATE / ACCESS RESTRICTED`.
2. **Simplified Elasticity Coefficients:** The matrix transmission coefficients represent general industrial averages. Actual corporate elasticities vary by sector capital intensity, regulatory constraints, and contracts.
3. **Exogenous Market Shocks:** The model assumes ceteris paribus (constant macro interest rates, inflation, and sovereign tax regimes) during the projection window.
