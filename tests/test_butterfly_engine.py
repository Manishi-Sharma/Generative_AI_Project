import pytest
from modules.butterfly_engine import ButterflyEffectEngine

def test_butterfly_engine_initialization():
    engine = ButterflyEffectEngine()
    assert len(engine.VARIABLES) == 10
    assert engine.graph.number_of_nodes() == 10
    assert engine.graph.number_of_edges() > 15
    assert engine.W.shape == (10, 10)

def test_butterfly_engine_cost_reduction_simulation():
    engine = ButterflyEffectEngine()

    # Simulate 5% reduction in Operating Expenses
    baselines = {
        "Revenue": 100000.0,
        "Operating Expenses": 70000.0,
        "Operating Profit": 30000.0,
        "Net Profit": 22000.0,
        "Cash Reserves": 15000.0
    }

    sim = engine.simulate(
        initial_var="Operating Expenses",
        initial_change_pct=-5.0,
        time_horizon="1 Year",
        dampening=0.60,
        baselines=baselines
    )

    assert sim["initial_variable"] == "Operating Expenses"
    assert sim["initial_change_pct"] == -5.0
    assert "variable_results" in sim

    var_res = sim["variable_results"]

    # Operating Profit should show a positive shift due to inverse relationship
    op_profit_res = var_res["Operating Profit"]
    assert op_profit_res["cumulative_delta_pct"] > 0.0

    # Net Profit should also reflect positive ripple
    assert var_res["Net Profit"]["cumulative_delta_pct"] > 0.0

    # Simulated values should be computed where baseline exists
    assert op_profit_res["simulated_value"] is not None
    assert op_profit_res["simulated_value"] > baselines["Operating Profit"]

    # Verify dampening prevents uncontrolled explosion
    for v, r in var_res.items():
        assert -100.0 <= r["cumulative_delta_pct"] <= 300.0

    # Verify positive and negative consequence identification
    assert len(sim["positive_consequences"]) > 0
    assert len(sim["assumptions"]) > 0

def test_butterfly_engine_invalid_variable_raises():
    engine = ButterflyEffectEngine()
    with pytest.raises(ValueError):
        engine.simulate("NonExistentVariable", 10.0)

def test_butterfly_engine_plotly_figures():
    engine = ButterflyEffectEngine()
    sim = engine.simulate("Revenue", 10.0, "1 Year")
    fig_net = engine.generate_plotly_network(sim)
    assert fig_net is not None
    fig_comp = engine.generate_comparison_chart(sim)
    assert fig_comp is not None
