"""
The Financial Butterfly Effect Mathematical Engine.
Implements a directed weighted financial dependency graph using NetworkX,
matrix ripple propagation (delta_next = A @ delta_current), feedback damping,
saturation bounds, and multi-order causal ripple analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
import numpy as np
import pandas as pd


# 12 Core Financial Nodes
NODES = [
    "Revenue",
    "Operating Expenses",
    "Cash Reserves",
    "Investment Capital",
    "Employee Productivity",
    "Production Capacity",
    "Research and Development",
    "Marketing",
    "Profitability",
    "Liquidity",
    "Debt",
    "Organisational Growth",
]

NODE_INDEX = {name: i for i, name in enumerate(NODES)}


# Documented Economic Causal Dependencies
DEFAULT_DEPENDENCIES = [
    # (source, target, weight, description, is_positive)
    ("Operating Expenses", "Profitability", -0.85, "Cost reductions immediately lift operating profit margins", False),
    ("Operating Expenses", "Cash Reserves", -0.70, "Lower operating outflow preserves liquid cash reserves", False),
    ("Operating Expenses", "Employee Productivity", 0.40, "Deep expense cuts (salaries, training, tooling) diminish staff morale and productivity", True),
    ("Operating Expenses", "Production Capacity", 0.35, "Depriving operations of budget constrains throughput and maintenance capacity", True),
    ("Cash Reserves", "Liquidity", 0.90, "Higher liquid cash directly bolsters quick and current liquidity ratios", True),
    ("Cash Reserves", "Investment Capital", 0.65, "Surplus unencumbered cash expands capacity for capital allocation", True),
    ("Cash Reserves", "Debt", -0.45, "Ample cash reserves allow retiring high-interest debt and credit facilities", False),
    ("Investment Capital", "Research and Development", 0.60, "Capital allocation funds new technology, automation, and R&D pipelines", True),
    ("Investment Capital", "Organisational Growth", 0.65, "Productive investments accelerate physical, digital, and market expansion", True),
    ("Research and Development", "Employee Productivity", 0.50, "Process innovation and modern tools elevate productivity per worker", True),
    ("Research and Development", "Revenue", 0.45, "Proprietary product improvements command pricing power and market share", True),
    ("Marketing", "Revenue", 0.65, "Strategic customer acquisition campaigns directly drive top-line revenue", True),
    ("Marketing", "Operating Expenses", 0.80, "Advertising and marketing campaigns add directly to operational expenditures", True),
    ("Employee Productivity", "Production Capacity", 0.60, "A motivated and productive workforce maximizes unit throughput", True),
    ("Employee Productivity", "Operating Expenses", -0.25, "High productivity minimizes rework, idle time, and overtime penalties", False),
    ("Production Capacity", "Revenue", 0.70, "Greater operational capacity allows meeting surges in market demand", True),
    ("Revenue", "Profitability", 0.90, "Gross sales volume directly drives the bottom-line profitability pool", True),
    ("Revenue", "Cash Reserves", 0.65, "Top-line cash collections replenish liquid treasury reserves", True),
    ("Profitability", "Cash Reserves", 0.75, "Retained earnings accumulate into permanent liquid treasury balances", True),
    ("Profitability", "Organisational Growth", 0.70, "Consistently profitable enterprises reinvest free cash flow into scaling", True),
    ("Debt", "Liquidity", -0.65, "Heavy debt amortization drains current working capital and liquidity", False),
    ("Debt", "Operating Expenses", 0.30, "Interest expenses and financing costs inflate recurring fixed overhead", True),
    ("Liquidity", "Organisational Growth", 0.35, "Solvent balance sheets enable seizing opportunistic market acquisitions", True),
    ("Organisational Growth", "Revenue", 0.55, "Expanded geographical and customer footprint yields compounding revenue", True),
]


class ButterflyEngine:
    """
    Mathematical Financial Ripple-Effect Engine.
    Constructs the directed dependency graph, builds matrix A,
    and runs bounded multi-period simulations.
    """

    def __init__(self, custom_dependencies: Optional[List[Tuple[str, str, float, str, bool]]] = None):
        self.nodes = NODES
        self.node_index = NODE_INDEX
        self.num_nodes = len(self.nodes)
        self.dependencies = custom_dependencies or DEFAULT_DEPENDENCIES
        self.graph = self._build_graph()
        self.adjacency_matrix = self._build_matrix()

    def _build_graph(self) -> nx.DiGraph:
        """Constructs a NetworkX DiGraph with nodes and weighted directed causal edges."""
        G = nx.DiGraph()
        for node in self.nodes:
            G.add_node(node)

        for src, tgt, weight, desc, is_pos in self.dependencies:
            if src in self.node_index and tgt in self.node_index:
                G.add_edge(src, tgt, weight=weight, description=desc, is_positive=is_pos)
        return G

    def _build_matrix(self) -> np.ndarray:
        """Constructs adjacency matrix A where A[tgt, src] = weight."""
        A = np.zeros((self.num_nodes, self.num_nodes), dtype=np.float64)
        for u, v, data in self.graph.edges(data=True):
            src_idx = self.node_index[u]
            tgt_idx = self.node_index[v]
            A[tgt_idx, src_idx] = data.get("weight", 0.0)
        return A

    def calculate_ripple(
        self,
        initial_shocks: Dict[str, float],
        scenario_multiplier: float = 1.0,
        damping_factor: float = 0.85,
        max_periods: int = 5,
    ) -> Dict[str, Any]:
        """
        Executes multi-order and multi-period ripple propagation.

        Model:
        delta_0 = initial shock vector (Order 0)
        delta_1 = A @ delta_0 (First-order downstream)
        delta_2 = A @ delta_1 (Second-order downstream)
        
        Multi-period evolution:
        delta_{t+1} = gamma * tanh( A @ delta_t ) + nonlinear_feedback(delta_t)
        """
        delta_0 = np.zeros(self.num_nodes, dtype=np.float64)
        for node_name, shock_pct in initial_shocks.items():
            if node_name in self.node_index:
                delta_0[self.node_index[node_name]] = float(shock_pct)

        # Scale matrix by scenario sensitivity (Optimistic, Baseline, Pessimistic)
        A_eff = self.adjacency_matrix * scenario_multiplier

        # Order 0: Direct User Decisions
        direct_impact = {node: delta_0[self.node_index[node]] for node in self.nodes if delta_0[self.node_index[node]] != 0}

        # Order 1: First-Order Consequences
        delta_1 = A_eff @ delta_0
        first_order = {self.nodes[i]: float(delta_1[i]) for i in range(self.num_nodes) if abs(delta_1[i]) > 1e-4}

        # Order 2: Second-Order Downstream Repercussions
        delta_2 = A_eff @ delta_1
        second_order = {self.nodes[i]: float(delta_2[i]) for i in range(self.num_nodes) if abs(delta_2[i]) > 1e-4}

        # Multi-Period Simulation over T years
        # Keep track of cumulative delta trajectories
        trajectories: Dict[str, List[float]] = {node: [] for node in self.nodes}
        period_names = [f"Year {t}" for t in range(1, max_periods + 1)]

        current_delta = delta_0.copy()
        cumulative_state = np.zeros(self.num_nodes, dtype=np.float64)

        for t in range(max_periods):
            # Compute raw next-period change
            raw_next = A_eff @ current_delta

            # Non-linear threshold feedback penalty:
            # If Operating Expenses are cut by > 10% (delta < -0.10),
            # productivity drops non-linearly due to severe organizational stress
            opex_idx = self.node_index["Operating Expenses"]
            prod_idx = self.node_index["Employee Productivity"]
            if current_delta[opex_idx] < -0.10:
                severe_cut = abs(current_delta[opex_idx]) - 0.10
                raw_next[prod_idx] -= severe_cut * 0.75  # Damaging penalty

            # Apply bounded damping using tanh to prevent runaway explosions
            # Ensures realistic percentage movements
            next_delta = damping_factor * np.tanh(raw_next)

            # Cumulative state integrates the period deltas with natural mean-reversion
            cumulative_state = 0.90 * cumulative_state + next_delta

            for i, node in enumerate(self.nodes):
                trajectories[node].append(float(cumulative_state[i]))

            current_delta = next_delta

        # Filter positive and negative consequences
        positive_consequences = []
        negative_consequences = []

        for node in self.nodes:
            net_change = trajectories[node][-1]
            if abs(net_change) < 0.005:
                continue

            # Contextualize polarity (for expenses and debt, reduction is positive)
            if node in ["Operating Expenses", "Debt"]:
                is_benefit = net_change < 0
            else:
                is_benefit = net_change > 0

            desc_text = f"{node}: {net_change:+.1%} cumulative 5-year impact"
            if is_benefit:
                positive_consequences.append(desc_text)
            else:
                negative_consequences.append(desc_text)

        # Build causal explanations
        causal_chains = self._explain_causal_chains(initial_shocks)

        return {
            "initial_shocks": initial_shocks,
            "direct_impact": direct_impact,
            "first_order_effects": first_order,
            "second_order_effects": second_order,
            "trajectories": trajectories,
            "period_names": period_names,
            "positive_consequences": positive_consequences,
            "negative_consequences": negative_consequences,
            "causal_chains": causal_chains,
            "final_5yr_deltas": {node: trajectories[node][-1] for node in self.nodes},
        }

    def _explain_causal_chains(self, initial_shocks: Dict[str, float]) -> List[str]:
        """Generates step-by-step human-readable explanations of active ripple chains."""
        chains = []
        for shock_node, shock_val in initial_shocks.items():
            if abs(shock_val) < 1e-4 or shock_node not in self.graph:
                continue

            direction = "decreased" if shock_val < 0 else "increased"
            chains.append(f"Decision: {shock_node} is {direction} by {abs(shock_val):.1%}.")

            # Downstream immediate successors
            successors = list(self.graph.successors(shock_node))
            for succ in successors:
                edge_data = self.graph.get_edge_data(shock_node, succ)
                weight = edge_data["weight"]
                succ_effect = shock_val * weight
                succ_dir = "expands" if succ_effect > 0 else "contracts"
                desc = edge_data.get("description", "")
                chains.append(
                    f"  ↳ Direct Effect: {succ} {succ_dir} by {abs(succ_effect):.1%} ({desc})."
                )

                # 2nd order downstream paths
                second_succs = list(self.graph.successors(succ))[:2]
                for s2 in second_succs:
                    if s2 == shock_node:
                        continue
                    e2 = self.graph.get_edge_data(succ, s2)
                    w2 = e2["weight"]
                    s2_effect = succ_effect * w2
                    s2_dir = "improves" if s2_effect > 0 else "degrades"
                    chains.append(
                        f"     ↳ Ripple Consequence: {s2} {s2_dir} by {abs(s2_effect):.1%} ({e2.get('description', '')})."
                    )
        return chains

    def simulate_scenarios(
        self,
        initial_shocks: Dict[str, float],
        base_financials: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Runs and compares 3 standard macro scenarios:
        1. Baseline: standard theoretical sensitivity
        2. Optimistic: +20% favorable elasticity and higher investment yields
        3. Pessimistic: -25% market friction, amplified operational risk
        """
        scenarios = {
            "Baseline": {"multiplier": 1.0, "damping": 0.85},
            "Optimistic": {"multiplier": 1.20, "damping": 0.90},
            "Pessimistic": {"multiplier": 0.80, "damping": 0.80},
        }

        results = {}
        base_rev = base_financials.get("revenue", 10_000_000.0)
        base_exp = base_financials.get("operating_expenses", 7_500_000.0)
        base_cash = base_financials.get("cash_reserves", 2_500_000.0)
        base_assets = base_financials.get("assets", 15_000_000.0)
        base_liab = base_financials.get("liabilities", 5_000_000.0)

        for sc_name, sc_params in scenarios.items():
            sim = self.calculate_ripple(
                initial_shocks=initial_shocks,
                scenario_multiplier=sc_params["multiplier"],
                damping_factor=sc_params["damping"],
                max_periods=5,
            )
            deltas = sim["final_5yr_deltas"]

            proj_rev = base_rev * (1.0 + deltas.get("Revenue", 0.0))
            proj_exp = base_exp * (1.0 + deltas.get("Operating Expenses", 0.0))
            proj_cash = base_cash * (1.0 + deltas.get("Cash Reserves", 0.0))
            proj_profit = proj_rev - proj_exp

            proj_assets = base_assets * (1.0 + deltas.get("Organisational Growth", 0.0) * 0.5)
            proj_liab = base_liab * (1.0 + deltas.get("Debt", 0.0))
            curr_ratio = proj_assets / proj_liab if proj_liab > 0 else 99.9

            results[sc_name] = {
                "Revenue": round(proj_rev, 2),
                "Operating Expenses": round(proj_exp, 2),
                "Net Profit": round(proj_profit, 2),
                "Cash Reserves": round(proj_cash, 2),
                "Liquidity Ratio": round(curr_ratio, 2),
            }

        return results
