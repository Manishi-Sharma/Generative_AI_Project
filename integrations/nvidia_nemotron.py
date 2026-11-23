import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL

logger = logging.getLogger(__name__)

class NemotronExplainer:
    """
    NVIDIA Nemotron LLM integration via NVIDIA NIM API.
    Interprets deterministic financial calculations, explains ripple effects,
    and delineates verified facts from simulation assumptions.
    """
    def __init__(self, api_key: str = NVIDIA_API_KEY, base_url: str = NVIDIA_BASE_URL, model: str = NVIDIA_MODEL):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model = model.strip()
        self._client: Optional[OpenAI] = None

        if self.api_key:
            try:
                self._client = OpenAI(
                    base_url=self.base_url,
                    api_key=self.api_key
                )
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client for NVIDIA NIM: {e}")

    def is_configured(self) -> bool:
        return bool(self._client and self.api_key)

    def explain_simulation(
        self,
        org_name: str,
        company_profile: Dict[str, Any],
        retrieved_financials: List[Dict[str, Any]],
        calculations: Dict[str, Any],
        simulation_result: Dict[str, Any]
    ) -> str:
        """
        Calls NVIDIA Nemotron to generate a structured financial interpretation.
        Falls back to a structured deterministic analysis if API key is not present or API call fails.
        """
        init_var = simulation_result.get("initial_variable", "Financial Variable")
        init_change = simulation_result.get("initial_change_pct", 0.0)
        time_horizon = simulation_result.get("time_horizon", "1 Year")
        var_results = simulation_result.get("variable_results", {})
        pos_effects = simulation_result.get("positive_consequences", [])
        neg_effects = simulation_result.get("negative_consequences", [])

        # Format financials for prompt
        fin_summary = []
        for f in retrieved_financials:
            val_str = f"{f.get('value'):,.2f} {f.get('currency', 'USD')}" if f.get("value") is not None else "Not Disclosed"
            fin_summary.append(f"- {f.get('metric_name')}: {val_str} (Status: {f.get('status')})")
        fin_text = "\n".join(fin_summary)

        # Format calculations
        calc_summary = []
        for k, v in calculations.items():
            if v.get("value") is not None:
                calc_summary.append(f"- {k}: {v.get('value'):.2f}{v.get('unit', '')} [Formula: {v.get('formula')}]")
        calc_text = "\n".join(calc_summary) if calc_summary else "No ratios calculated due to incomplete reported baseline."

        # Format simulation shift
        sim_summary = []
        for var, res in var_results.items():
            cum = res.get("cumulative_delta_pct", 0.0)
            sim_summary.append(f"- {var}: Cumulative Shift {cum:+.2f}%")
        sim_text = "\n".join(sim_summary)

        system_prompt = (
            "You are an expert corporate financial analyst and quantitative economist. "
            "Your objective is to interpret deterministic financial calculations and explain "
            "the 'Financial Butterfly Effect' (ripple-effect propagation) for an organisation. "
            "STRICT RULES:\n"
            "1. You must NEVER invent, fabricate, or hallucinate missing financial figures.\n"
            "2. Distinguish clearly between VERIFIED FACTS (retrieved from public reports), "
            "MATHEMATICAL CALCULATIONS (computed via deterministic formulas), "
            "MODEL ASSUMPTIONS, and HYPOTHETICAL SIMULATION OUTCOMES.\n"
            "3. NEVER describe a hypothetical simulation scenario as an actual company decision.\n"
            "4. Keep your explanations analytical, objective, and structured."
        )

        user_prompt = f"""
ORGANISATION CONTEXT:
Name: {org_name}
Country: {company_profile.get('country', 'Global')}
Industry: {company_profile.get('industry', 'Enterprise')}
Website: {company_profile.get('website', 'N/A')}
Ticker / Exchange: {company_profile.get('ticker', 'N/A')} ({company_profile.get('stock_exchange', 'N/A')})

VERIFIED PUBLIC FINANCIAL DATA:
{fin_text}

DETERMINISTIC FINANCIAL RATIOS:
{calc_text}

HYPOTHETICAL BUTTERFLY EFFECT SCENARIO:
Initial Hypothetical Perturbation: Adjust {init_var} by {init_change:+.2f}%
Time Horizon: {time_horizon}

DETERMINISTIC SIMULATION PROPAGATION RESULTS:
{sim_text}

IDENTIFIED DIRECT POSITIVE CONSEQUENCES:
{chr(10).join(pos_effects) if pos_effects else 'None significant'}

IDENTIFIED DIRECT NEGATIVE CONSEQUENCES & RISKS:
{chr(10).join(neg_effects) if neg_effects else 'None significant'}

Please provide a comprehensive analytical report containing the following exact sections:
1. EXECUTIVE INTERPRETATION OF INITIAL FINANCIAL DECISION
2. DIRECT / FIRST-ORDER IMPACT MECHANICS
3. BUTTERFLY EFFECT: HOW THE SHOCK SPREADS (SECOND-ORDER & FEEDBACK LOOPS)
4. BALANCE OF POSITIVE OPPORTUNITIES VS. FINANCIAL RISKS
5. SENSITIVITY, ASSUMPTIONS & UNCERTAINTIES
6. STRATEGIC TAKEAWAYS & GOVERNANCE CONSIDERATIONS
"""

        if self._client:
            try:
                logger.info(f"Dispatching simulation analysis to NVIDIA Nemotron NIM ({self.model})...")
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2,
                    max_tokens=2048,
                    timeout=30
                )
                content = response.choices[0].message.content
                if content and len(content.strip()) > 100:
                    return content
            except Exception as e:
                logger.error(f"NVIDIA Nemotron API invocation failed: {e}. Falling back to deterministic analytical generator.")

        # Fallback to structured deterministic analysis
        return self._generate_deterministic_analysis(
            org_name=org_name,
            init_var=init_var,
            init_change=init_change,
            time_horizon=time_horizon,
            var_results=var_results,
            pos_effects=pos_effects,
            neg_effects=neg_effects,
            calculations=calculations
        )

    def _generate_deterministic_analysis(
        self,
        org_name: str,
        init_var: str,
        init_change: float,
        time_horizon: str,
        var_results: Dict[str, Any],
        pos_effects: List[str],
        neg_effects: List[str],
        calculations: Dict[str, Any]
    ) -> str:
        """
        Deterministic, audit-compliant analytical interpretation when API key is unavailable.
        """
        direction = "reduction" if init_change < 0 else "increase"
        op_prof_shift = var_results.get("Operating Profit", {}).get("cumulative_delta_pct", 0.0)
        net_prof_shift = var_results.get("Net Profit", {}).get("cumulative_delta_pct", 0.0)
        cash_shift = var_results.get("Cash Reserves", {}).get("cumulative_delta_pct", 0.0)
        debt_shift = var_results.get("Debt", {}).get("cumulative_delta_pct", 0.0)
        growth_shift = var_results.get("Business Growth", {}).get("cumulative_delta_pct", 0.0)

        report = f"""### 1. EXECUTIVE INTERPRETATION OF INITIAL FINANCIAL DECISION
The modeled scenario simulates a hypothetical **{init_change:+.2f}% {direction}** in **{init_var}** for **{org_name}** over a **{time_horizon}** horizon.
In corporate financial mechanics, adjusting {init_var} introduces an immediate structural shift in working capital and operational resource allocation. This perturbation is treated purely as a simulation exercise and does not represent an announced management strategy.

### 2. DIRECT / FIRST-ORDER IMPACT MECHANICS
The primary shock to {init_var} immediately alters the income and expenditure balances:
- **Immediate Operating Profit Shift:** {op_prof_shift:+.2f}%
- **Immediate Net Profit Shift:** {net_prof_shift:+.2f}%
Direct cost-benefit transmission occurs through standard managerial accounting relationships. For instance, modifying expenditures changes the operational margin directly before any dynamic behavioral or customer adjustments manifest.

### 3. BUTTERFLY EFFECT: HOW THE SHOCK SPREADS (SECOND-ORDER & FEEDBACK LOOPS)
As time progresses through the {time_horizon} timeline, the initial decision ripples across the enterprise financial network:
- **Cash Reserves Impact:** Projected cumulative delta of **{cash_shift:+.2f}%**, reflecting the net cumulative change in retained operating liquidity.
- **Balance Sheet Leverage (Debt):** Estimated delta of **{debt_shift:+.2f}%**, caused by altered external financing reliance.
- **Enterprise Growth Headroom:** Projected change of **{growth_shift:+.2f}%** in business expansion capacity, governed by reinvestable retained earnings and capital expenditure headroom.

### 4. BALANCE OF POSITIVE OPPORTUNITIES VS. FINANCIAL RISKS
**Key Positive Ripple Consequences:**
{chr(10).join([f"- {p}" for p in pos_effects]) if pos_effects else "- Stability maintained without excessive volatility."}

**Key Risk Factors & Negative Ripple Consequences:**
{chr(10).join([f"- {n}" for n in neg_effects]) if neg_effects else "- No severe capital erosion identified under baseline dampening."}

### 5. SENSITIVITY, ASSUMPTIONS & UNCERTAINTIES
- **Model Assumptions:** Inter-variable elasticity coefficients are established using generalized industrial cost structures.
- **Dampening & Convergence:** A numerical dampening coefficient was applied to simulate organizational friction and avoid runaway feedback loops.
- **Exogenous Variables:** The simulation assumes that interest rate benchmarks, tax rates, and macro industry demand remain constant during the evaluation window.

### 6. STRATEGIC TAKEAWAYS & GOVERNANCE CONSIDERATIONS
A seemingly minor adjustment of {init_change:+.2f}% in {init_var} demonstrates the non-linear interconnectedness of balance sheet assets, cash conversion cycles, and expansion capability. Corporate executives and financial planners must evaluate such decisions holistically rather than in accounting silos.
"""
        return report
