import pytest
from modules.financial_calculations import FinancialCalculator

def test_financial_calculator_complete_inputs():
    test_metrics = {
        "Revenue": 1000000.0,
        "Operating Expenses": 600000.0,
        "Operating Profit": 400000.0,
        "Net Profit": 300000.0,
        "Total Assets": 2000000.0,
        "Shareholders' Equity": 1200000.0,
        "Borrowings (Debt)": 500000.0,
        "Cash and Cash Equivalents": 250000.0,
        "Operating Cash Flow": 350000.0,
        "Capital Expenditure": 100000.0
    }

    calcs = FinancialCalculator.calculate_all(test_metrics)

    # Operating Margin = (400,000 / 1,000,000) * 100 = 40.0%
    assert calcs["Operating Margin"]["status"] == "Computed"
    assert calcs["Operating Margin"]["value"] == 40.0

    # Net Profit Margin = (300,000 / 1,000,000) * 100 = 30.0%
    assert calcs["Net Profit Margin"]["status"] == "Computed"
    assert calcs["Net Profit Margin"]["value"] == 30.0

    # ROA = (300,000 / 2,000,000) * 100 = 15.0%
    assert calcs["Return on Assets (ROA)"]["status"] == "Computed"
    assert calcs["Return on Assets (ROA)"]["value"] == 15.0

    # ROE = (300,000 / 1,200,000) * 100 = 25.0%
    assert calcs["Return on Equity (ROE)"]["status"] == "Computed"
    assert calcs["Return on Equity (ROE)"]["value"] == 25.0

    # Debt-to-Equity = 500,000 / 1,200,000 = ~0.4167
    assert calcs["Debt-to-Equity Ratio"]["status"] == "Computed"
    assert round(calcs["Debt-to-Equity Ratio"]["value"], 3) == 0.417

    # Free Cash Flow = 350,000 - 100,000 = 250,000
    assert calcs["Free Cash Flow (FCF)"]["status"] == "Computed"
    assert calcs["Free Cash Flow (FCF)"]["value"] == 250000.0

def test_financial_calculator_missing_inputs_never_assumes_zero():
    # Only revenue provided; net profit and debt are missing
    partial_metrics = {
        "Revenue": 500000.0,
        "Total Assets": 1000000.0
    }
    calcs = FinancialCalculator.calculate_all(partial_metrics)

    # Operating margin should be incomplete, not zero
    assert calcs["Operating Margin"]["status"] == "Inputs Incomplete"
    assert calcs["Operating Margin"]["value"] is None
    assert "Operating Profit" in calcs["Operating Margin"]["missing"]

    # ROA requires Net Profit, so should be incomplete
    assert calcs["Return on Assets (ROA)"]["status"] == "Inputs Incomplete"
    assert calcs["Return on Assets (ROA)"]["value"] is None
