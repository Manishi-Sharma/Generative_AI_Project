import networkx as nx
import numpy as np
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple

class ButterflyEffectEngine:
    """
    Financial Ripple-Effect & Dependency Simulation Engine.
    Models interconnected corporate financial variables using a directed NetworkX graph
    and a stabilized matrix multiplication propagation model:
    change_next = dampening * (dependency_matrix @ change_current)
    """

    VARIABLES = [
        "Revenue",
        "Operating Expenses",
        "Operating Profit",
        "Net Profit",
        "Cash Flow",
        "Cash Reserves",
        "Debt",
        "Investment Capacity",
        "Capital Expenditure",
        "Business Growth"
    ]

    # Directed dependency edges: (Source, Target, Coefficient, Rationale)
    # Coefficient > 0 means positive correlation; < 0 means inverse relationship.
    EDGES = [
        ("Revenue", "Operating Profit", 0.75, "Incremental revenue directly drops to operating profit after variable costs."),
        ("Revenue", "Cash Flow", 0.65, "Higher sales generate cash receipts through customer collections."),
        ("Revenue", "Business Growth", 0.40, "Top-line expansion drives market share and operational scale."),

        ("Operating Expenses", "Operating Profit", -0.85, "Higher operational expenditures directly depress operating margin."),
        ("Operating Expenses", "Cash Flow", -0.70, "Operational expenses require immediate working capital outflows."),
        ("Operating Expenses", "Investment Capacity", -0.30, "Excess overhead absorbs discretionary liquid funds."),

        ("Operating Profit", "Net Profit", 0.80, "Operating earnings flow through to net income after interest and corporate taxes."),

        ("Net Profit", "Cash Reserves", 0.60, "Retained earnings accumulate into liquid cash balances."),
        ("Net Profit", "Investment Capacity", 0.75, "Bottom-line profitability expands internal capital financing headroom."),

        ("Cash Flow", "Cash Reserves", 0.85, "Operating cash inflows directly bolster liquid treasury reserves."),
        ("Cash Flow", "Debt", -0.35, "Strong cash generation enables scheduled debt principal reduction."),
        ("Cash Flow", "Investment Capacity", 0.50, "Consistent cash generation improves borrowing power and solvency."),

        ("Cash Reserves", "Investment Capacity", 0.70, "Unencumbered cash provides immediate self-funded expansion capability."),
        ("Cash Reserves", "Debt", -0.20, "Surplus liquidity can be deployed to retire high-cost credit lines."),

        ("Debt", "Net Profit", -0.30, "Higher borrowings increase mandatory interest expense burdens."),
        ("Debt", "Cash Reserves", 0.45, "Debt issuance injects gross cash proceeds into balance sheet."),
        ("Debt", "Investment Capacity", -0.40, "Excessive financial leverage constrains additional credit facilities."),

        ("Capital Expenditure", "Cash Reserves", -0.75, "Asset investments require upfront cash disbursement."),
        ("Capital Expenditure", "Debt", 0.35, "Large capex projects are partially funded through debt instruments."),
        ("Capital Expenditure", "Business Growth", 0.60, "Productive asset investments increase future output capacity."),

        ("Investment Capacity", "Capital Expenditure", 0.50, "Greater capital headroom enables strategic expansion initiatives."),
        ("Investment Capacity", "Business Growth", 0.45, "Resource flexibility empowers market capture and new product launches."),

        ("Business Growth", "Revenue", 0.60, "Enlarged market footprint drives future sales volume."),
        ("Business Growth", "Operating Expenses", 0.35, "Scale expansion requires additional staffing and operational infrastructure.")
    ]

    def __init__(self):
        self.graph = nx.DiGraph()
        for v in self.VARIABLES:
            self.graph.add_node(v)

        for src, dst, coeff, rationale in self.EDGES:
            self.graph.add_edge(src, dst, weight=coeff, rationale=rationale)

        # Build numerical dependency matrix W of shape (N, N) where W[i, j] = effect of j on i
        self.n = len(self.VARIABLES)
        self.var_to_idx = {v: i for i, v in enumerate(self.VARIABLES)}
        self.idx_to_var = {i: v for i, v in enumerate(self.VARIABLES)}
        self.W = np.zeros((self.n, self.n), dtype=np.float64)

        for src, dst, coeff, _ in self.EDGES:
            i = self.var_to_idx[dst]
            j = self.var_to_idx[src]
            self.W[i, j] = coeff

    def simulate(
        self,
        initial_var: str,
        initial_change_pct: float,
        time_horizon: str = "1 Year",
        dampening: float = 0.60,
        baselines: Optional[Dict[str, Optional[float]]] = None
    ) -> Dict[str, Any]:
        """
        Executes step-by-step ripple simulation with mathematical stabilization.
        Preventing exponential explosion via dampening factor lambda < 1.0.
        """
        if initial_var not in self.var_to_idx:
            raise ValueError(f"Variable '{initial_var}' not recognized in simulation model.")

        # Horizon steps
        horizon_steps_map = {
            "1 Quarter": 1,
            "2 Quarters": 2,
            "1 Year": 3,
            "2 Years": 4,
            "3 Years": 5,
            "5 Years": 6
        }
        num_steps = horizon_steps_map.get(time_horizon, 3)

        # Vector of state changes at each step
        delta_history = []
        change_current = np.zeros(self.n, dtype=np.float64)
        init_idx = self.var_to_idx[initial_var]
        change_current[init_idx] = initial_change_pct
        delta_history.append(change_current.copy())

        # Propagate step by step: change_next = dampening * (W @ change_current)
        for step in range(1, num_steps + 1):
            change_next = dampening * (self.W @ change_current)
            # Cap extreme shifts to ensure realistic bounds (-100% to +300%)
            change_next = np.clip(change_next, -100.0, 300.0)
            delta_history.append(change_next.copy())
            change_current = change_next

        # Total cumulative delta across all steps
        cumulative_deltas = np.sum(delta_history, axis=0)

        # Baseline alignment
        baselines = baselines or {}
        variable_results = {}
        for i, var_name in enumerate(self.VARIABLES):
            cum_pct = float(cumulative_deltas[i])
            base_val = baselines.get(var_name)
            sim_val = None
            if base_val is not None:
                sim_val = base_val * (1.0 + cum_pct / 100.0)

            variable_results[var_name] = {
                "initial_delta_pct": float(delta_history[0][i]),
                "step1_direct_pct": float(delta_history[1][i]) if len(delta_history) > 1 else 0.0,
                "step2_ripple_pct": float(delta_history[2][i]) if len(delta_history) > 2 else 0.0,
                "cumulative_delta_pct": cum_pct,
                "baseline_value": base_val,
                "simulated_value": sim_val
            }

        # Detailed step breakdowns with rationales
        step_narratives = []
        step_narratives.append({
            "step": 0,
            "title": "Initial Hypothetical Decision",
            "impacts": [{
                "variable": initial_var,
                "change_pct": initial_change_pct,
                "description": f"User-specified baseline perturbation of {initial_change_pct:+.2f}% applied to {initial_var}."
            }]
        })

        for s in range(1, len(delta_history)):
            step_deltas = delta_history[s]
            notable = []
            for i, d in enumerate(step_deltas):
                if abs(d) >= 0.05:  # Significant shift threshold
                    var = self.idx_to_var[i]
                    # Find driving incoming edges from previous step
                    drivers = []
                    prev_step = delta_history[s - 1]
                    for src, dst, data in self.graph.in_edges(var, data=True):
                        src_idx = self.var_to_idx[src]
                        if abs(prev_step[src_idx]) >= 0.05:
                            drivers.append(f"{src} ({prev_step[src_idx]:+.1f}%) -> {data.get('rationale')}")

                    notable.append({
                        "variable": var,
                        "change_pct": float(d),
                        "drivers": drivers
                    })

            step_title = "Immediate Direct Financial Impact" if s == 1 else (
                "First-Order Ripple Effects" if s == 2 else f"Order-{s} Propagation & Feedback Effects"
            )
            step_narratives.append({
                "step": s,
                "title": step_title,
                "impacts": notable
            })

        # Categorize positive and negative consequences
        positive_effects = []
        negative_effects = []
        for var, res in variable_results.items():
            pct = res["cumulative_delta_pct"]
            if abs(pct) < 0.2:
                continue

            # Variable interpretation of positive vs negative
            # For Debt and Operating Expenses, reduction is generally positive
            if var in ["Debt", "Operating Expenses"]:
                if pct < 0:
                    positive_effects.append(f"{var} decreased by {abs(pct):.2f}% (improved cost efficiency / lower leverage).")
                else:
                    negative_effects.append(f"{var} increased by {pct:+.2f}% (higher cost burden / debt load).")
            else:
                if pct > 0:
                    positive_effects.append(f"{var} expanded by {pct:+.2f}% (favorable capacity / margin gain).")
                else:
                    negative_effects.append(f"{var} contracted by {abs(pct):.2f}% (downward pressure on profitability / resources).")

        return {
            "initial_variable": initial_var,
            "initial_change_pct": initial_change_pct,
            "time_horizon": time_horizon,
            "num_steps": num_steps,
            "variable_results": variable_results,
            "step_narratives": step_narratives,
            "positive_consequences": positive_effects,
            "negative_consequences": negative_effects,
            "assumptions": [
                "The matrix dependency model assumes stable market conditions without sudden exogenous macro shocks.",
                "Inter-variable transmission coefficients reflect general corporate finance mechanics and standard cost accounting behavior.",
                f"A stabilization dampening factor of lambda = {dampening} is applied per iteration to prevent unrealistic unbounded feedback.",
                "Hypothetical adjustments are simulation projections and do not reflect official corporate management forecasts."
            ]
        }

    def generate_plotly_network(self, sim_data: Dict[str, Any]) -> go.Figure:
        """
        Creates an interactive Plotly directed graph visualization of the financial butterfly effect.
        """
        pos = nx.circular_layout(self.graph)

        edge_x = []
        edge_y = []
        edge_annotations = []

        initial_var = sim_data["initial_variable"]
        var_results = sim_data["variable_results"]

        for edge in self.graph.edges(data=True):
            src, dst, data = edge
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            # Small arrow annotation
            coeff = data.get("weight", 0)
            color = "#00F5D4" if coeff > 0 else "#FF5964"

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1.2, color="rgba(100, 150, 220, 0.35)"),
            hoverinfo="none",
            mode="lines"
        )

        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []

        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            res = var_results.get(node, {})
            cum_pct = res.get("cumulative_delta_pct", 0.0)

            # Node styling
            if node == initial_var:
                node_colors.append("#7B2CBF") # Purple highlight for root shock
                node_sizes.append(42)
            elif cum_pct > 0.5:
                node_colors.append("#00F5D4") # Bright Teal / Green for positive
                node_sizes.append(34)
            elif cum_pct < -0.5:
                node_colors.append("#FF5964") # Coral / Red for negative
                node_sizes.append(34)
            else:
                node_colors.append("#4A90E2") # Neutral Blue
                node_sizes.append(28)

            hover_lbl = f"<b>{node}</b><br>Cumulative Shift: {cum_pct:+.2f}%"
            if res.get("baseline_value") is not None and res.get("simulated_value") is not None:
                hover_lbl += f"<br>Baseline: {res['baseline_value']:,.1f}<br>Simulated: {res['simulated_value']:,.1f}"
            node_text.append(hover_lbl)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            hoverinfo="text",
            text=[f"<b>{n}</b>" for n in self.graph.nodes()],
            textposition="top center",
            hovertext=node_text,
            textfont=dict(color="#FFFFFF", size=11, family="Inter, sans-serif"),
            marker=dict(
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color="#FFFFFF")
            )
        )

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text="<b>Financial Dependency Ripple Network (Directed Propagation Graph)</b>",
                    font=dict(color="#FEFCFB", size=16)
                ),
                showlegend=False,
                hovermode="closest",
                paper_bgcolor="#0A1128",
                plot_bgcolor="#0A1128",
                margin=dict(b=40, l=40, r=40, t=60),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=520
            )
        )
        return fig

    def generate_comparison_chart(self, sim_data: Dict[str, Any]) -> go.Figure:
        """
        Creates a grouped bar chart of baseline vs simulated figures for metrics with baseline data.
        """
        var_results = sim_data["variable_results"]
        categories = []
        baseline_vals = []
        simulated_vals = []

        for var, res in var_results.items():
            if res.get("baseline_value") is not None and res.get("simulated_value") is not None:
                categories.append(var)
                baseline_vals.append(res["baseline_value"])
                simulated_vals.append(res["simulated_value"])

        if not categories:
            # If no absolute baselines, display percentage deltas bar chart
            return self._generate_delta_pct_chart(sim_data)

        fig = go.Figure(data=[
            go.Bar(
                name="Baseline (Reported)",
                x=categories,
                y=baseline_vals,
                marker_color="#3A86FF"
            ),
            go.Bar(
                name="Simulated Scenario",
                x=categories,
                y=simulated_vals,
                marker_color="#00F5D4"
            )
        ])

        fig.update_layout(
            barmode="group",
            title=dict(
                text="<b>Baseline vs Simulated Scenario Comparison (Reported Currency)</b>",
                font=dict(color="#FEFCFB", size=16)
            ),
            paper_bgcolor="#0A1128",
            plot_bgcolor="#001F54",
            font=dict(color="#FEFCFB"),
            xaxis=dict(gridcolor="#1282A2"),
            yaxis=dict(gridcolor="#1282A2"),
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    def _generate_delta_pct_chart(self, sim_data: Dict[str, Any]) -> go.Figure:
        """Fallback chart when absolute baseline amounts are unrecorded."""
        var_results = sim_data["variable_results"]
        vars_list = list(var_results.keys())
        pcts = [var_results[v]["cumulative_delta_pct"] for v in vars_list]
        colors = ["#00F5D4" if p >= 0 else "#FF5964" for p in pcts]

        fig = go.Figure(data=[
            go.Bar(
                x=vars_list,
                y=pcts,
                marker_color=colors,
                text=[f"{p:+.1f}%" for p in pcts],
                textposition="auto"
            )
        ])
        fig.update_layout(
            title=dict(
                text="<b>Simulated Percentage Shift by Variable (Cumulative Ripple Effect)</b>",
                font=dict(color="#FEFCFB", size=16)
            ),
            paper_bgcolor="#0A1128",
            plot_bgcolor="#001F54",
            font=dict(color="#FEFCFB"),
            xaxis=dict(gridcolor="#1282A2"),
            yaxis=dict(gridcolor="#1282A2", title="Cumulative Change (%)"),
            height=420
        )
        return fig
