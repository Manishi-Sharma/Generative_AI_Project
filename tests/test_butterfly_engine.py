"""
Tests for the Financial Butterfly Effect mathematical engine.
Verifies directed graph topology, ripple propagation, damping, and non-linear penalties.
"""

import numpy as np
from modules.butterfly_engine import ButterflyEngine, NODES


def test_butterfly_engine_initialisation():
    engine = ButterflyEngine()
    assert len(engine.nodes) == 12
    assert engine.graph.number_of_nodes() == 12
    assert engine.graph.number_of_edges() > 15
    assert engine.adjacency_matrix.shape == (12, 12)


def test_ripple_propagation_and_order_effects():
    engine = ButterflyEngine()
    
    # 2% reduction in Operating Expenses
    initial_shocks = {"Operating Expenses": -0.02}
    sim = engine.calculate_ripple(initial_shocks=initial_shocks, max_periods=5)

    assert "Operating Expenses" in sim["direct_impact"]
    assert sim["direct_impact"]["Operating Expenses"] == -0.02

    # First-order: Profitability must rise, Cash Reserves must increase
    first_order = sim["first_order_effects"]
    assert "Profitability" in first_order
    assert first_order["Profitability"] > 0  # Lower opex -> higher profit

    # Second-order downstream
    second_order = sim["second_order_effects"]
    assert len(second_order) > 0


def test_engine_stability_and_boundedness():
    """Ensure that multi-period simulation does not explode exponentially."""
    engine = ButterflyEngine()
    
    # Large aggressive shocks
    initial_shocks = {
        "Operating Expenses": -0.30,
        "Investment Capital": 0.50,
        "Marketing": 0.40,
    }
    sim = engine.calculate_ripple(initial_shocks=initial_shocks, max_periods=5)

    trajectories = sim["trajectories"]
    for node, vals in trajectories.items():
        assert len(vals) == 5
        # Values must remain bounded within reasonable percentage bounds (-200% to +200%)
        for v in vals:
            assert -2.0 <= v <= 2.0, f"Node {node} value {v} exceeded stability bounds!"


def test_negative_consequences_severe_cut():
    """Verify that severe cost reductions (>10%) trigger productivity penalties."""
    engine = ButterflyEngine()
    
    # Severe 25% cut in operating expenses
    severe_shock = {"Operating Expenses": -0.25}
    sim = engine.calculate_ripple(initial_shocks=severe_shock, max_periods=5)

    # Long term employee productivity should drop due to organizational stress
    final_prod = sim["final_5yr_deltas"]["Employee Productivity"]
    assert final_prod < 0, f"Expected negative productivity penalty, got {final_prod}"
