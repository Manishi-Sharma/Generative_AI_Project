"""
Tests for financial calculations, ratios, interest, and currency formatting.
"""

from utils.calculations import (
    calculate_operating_profit,
    calculate_net_profit,
    calculate_profit_margin,
    calculate_current_ratio,
    calculate_debt_ratio,
    calculate_roi,
    calculate_simple_interest,
    calculate_compound_interest,
    calculate_npv,
    format_currency,
)


def test_profit_calculations():
    rev = 10_000_000.0
    opex = 7_500_000.0
    taxes = 500_000.0
    loan = 200_000.0

    op_profit = calculate_operating_profit(rev, opex)
    assert op_profit == 2_500_000.0

    net_profit = calculate_net_profit(op_profit, taxes, loan)
    assert net_profit == 1_800_000.0

    margin = calculate_profit_margin(net_profit, rev)
    assert margin == 18.0


def test_liquidity_and_debt_ratios():
    assets = 50_000_000.0
    liabilities = 20_000_000.0

    curr_ratio = calculate_current_ratio(assets, liabilities)
    assert curr_ratio == 2.5

    debt_ratio = calculate_debt_ratio(liabilities, assets)
    assert debt_ratio == 0.40

    # Zero protection
    assert calculate_current_ratio(assets, 0) == 99.99
    assert calculate_debt_ratio(liabilities, 0) == 1.0


def test_investment_calculations():
    principal = 1_000_000.0
    rate = 0.10  # 10%
    years = 2

    # Simple interest: 1,000,000 * 0.10 * 2 = 200,000
    si = calculate_simple_interest(principal, rate, years)
    assert si == 200_000.0

    # Compound interest: 1,000,000 * (1.10)^2 - 1,000,000 = 210,000
    ci = calculate_compound_interest(principal, rate, years, compounding_frequency=1)
    assert ci == 210_000.0

    # ROI on gain of 210,000
    roi = calculate_roi(principal + ci, principal)
    assert roi == 21.0

    # NPV: initial 1,000,000, cash flows [600,000, 600,000] at 10% discount rate
    npv = calculate_npv(0.10, 1_000_000.0, [600_000.0, 600_000.0])
    # PV = 600000/1.1 + 600000/1.21 = 545454.55 + 495867.77 = 1041322.31 - 1000000 = 41322.31
    assert round(npv, 0) == 41322.0


def test_currency_formatting():
    assert "₹1.00 Cr" == format_currency(10_000_000.0, "₹", abbreviate=True)
    assert "₹50.00 L" == format_currency(5_000_000.0, "₹", abbreviate=True)
    assert "₹1,00,00,000.00" == format_currency(10_000_000.0, "₹", abbreviate=False)
    assert "-₹50,000.00" == format_currency(-50_000.0, "₹", abbreviate=False)
