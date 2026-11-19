"""
Tests for NVIDIA NIM client and offline fallback mode.
Ensures zero-crash resilience even when external API credentials are absent.
"""

from modules.nvidia_client import NvidiaClient


def test_nvidia_client_initialisation_and_availability():
    # Test client without valid API key
    client = NvidiaClient(api_key="nvapi-your-key-here")
    is_avail, msg = client.is_available()
    assert is_avail is False
    assert "fallback" in msg.lower() or "not configured" in msg.lower()


def test_nvidia_client_deterministic_fallback():
    client = NvidiaClient(api_key="")
    
    # Query fallback response
    result = client.query(
        system_prompt="You are a financial analyst.",
        user_prompt="What happens if we reduce expenses by 5% and increase investment?",
    )
    assert result["success"] is True
    assert result["was_fallback"] is True
    assert "Butterfly Effect" in result["response"] or "Financial" in result["response"]
    assert len(result["response"]) > 100


def test_nvidia_client_butterfly_explanation():
    client = NvidiaClient(api_key="")
    shocks = {"Operating Expenses": -0.05, "Investment Capital": 0.10}
    ripple_results = {
        "first_order_effects": {"Profitability": 0.0425, "Cash Reserves": 0.035},
        "positive_consequences": ["Profitability: +4.3%", "Cash Reserves: +3.5%"],
        "negative_consequences": ["Employee Productivity: -1.2%"],
    }
    explanation = client.explain_butterfly_effect(shocks, ripple_results, "ABC Manufacturing Ltd.")
    assert explanation["success"] is True
    assert len(explanation["response"]) > 150
