from typing import Dict, Any, Optional

class FinancialCalculator:
    """
    Deterministic Python Financial Calculation Engine.
    Only computes ratios and metrics when all required inputs exist.
    Never assumes missing values are zero.
    """

    @staticmethod
    def calculate_all(metrics: Dict[str, Optional[float]]) -> Dict[str, Any]:
        """
        Executes all applicable financial ratios and returns results along with formulas.
        """
        results = {}

        # 1. Margins
        rev = metrics.get("Revenue")
        op_exp = metrics.get("Operating Expenses")
        op_profit = metrics.get("Operating Profit")
        net_profit = metrics.get("Net Profit")
        assets = metrics.get("Total Assets")
        equity = metrics.get("Shareholders' Equity")
        debt = metrics.get("Borrowings (Debt)")
        cash = metrics.get("Cash and Cash Equivalents")
        ocf = metrics.get("Operating Cash Flow")
        capex = metrics.get("Capital Expenditure")

        # Operating Margin
        if op_profit is not None and rev is not None and rev != 0:
            val = (op_profit / rev) * 100
            results["Operating Margin"] = {
                "value": val,
                "unit": "%",
                "formula": "(Operating Profit / Revenue) * 100",
                "inputs": {"Operating Profit": op_profit, "Revenue": rev},
                "status": "Computed",
                "interpretation": "Measures core operational profitability before interest and taxes."
            }
        else:
            results["Operating Margin"] = {
                "value": None,
                "unit": "%",
                "formula": "(Operating Profit / Revenue) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Operating Profit", op_profit), ("Revenue", rev)] if v is None]
            }

        # Net Profit Margin
        if net_profit is not None and rev is not None and rev != 0:
            val = (net_profit / rev) * 100
            results["Net Profit Margin"] = {
                "value": val,
                "unit": "%",
                "formula": "(Net Profit / Revenue) * 100",
                "inputs": {"Net Profit": net_profit, "Revenue": rev},
                "status": "Computed",
                "interpretation": "Percentage of revenue remaining as bottom-line profit."
            }
        else:
            results["Net Profit Margin"] = {
                "value": None,
                "unit": "%",
                "formula": "(Net Profit / Revenue) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Net Profit", net_profit), ("Revenue", rev)] if v is None]
            }

        # Operating Expense Ratio
        if op_exp is not None and rev is not None and rev != 0:
            val = (op_exp / rev) * 100
            results["Operating Expense Ratio"] = {
                "value": val,
                "unit": "%",
                "formula": "(Operating Expenses / Revenue) * 100",
                "inputs": {"Operating Expenses": op_exp, "Revenue": rev},
                "status": "Computed",
                "interpretation": "Operational cost efficiency relative to top-line turnover."
            }
        else:
            results["Operating Expense Ratio"] = {
                "value": None,
                "unit": "%",
                "formula": "(Operating Expenses / Revenue) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Operating Expenses", op_exp), ("Revenue", rev)] if v is None]
            }

        # Return on Assets (ROA)
        if net_profit is not None and assets is not None and assets != 0:
            val = (net_profit / assets) * 100
            results["Return on Assets (ROA)"] = {
                "value": val,
                "unit": "%",
                "formula": "(Net Profit / Total Assets) * 100",
                "inputs": {"Net Profit": net_profit, "Total Assets": assets},
                "status": "Computed",
                "interpretation": "Efficiency in generating net earnings from balance sheet assets."
            }
        else:
            results["Return on Assets (ROA)"] = {
                "value": None,
                "unit": "%",
                "formula": "(Net Profit / Total Assets) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Net Profit", net_profit), ("Total Assets", assets)] if v is None]
            }

        # Return on Equity (ROE)
        if net_profit is not None and equity is not None and equity != 0:
            val = (net_profit / equity) * 100
            results["Return on Equity (ROE)"] = {
                "value": val,
                "unit": "%",
                "formula": "(Net Profit / Shareholders' Equity) * 100",
                "inputs": {"Net Profit": net_profit, "Shareholders' Equity": equity},
                "status": "Computed",
                "interpretation": "Net profitability generated on shareholder capital."
            }
        else:
            results["Return on Equity (ROE)"] = {
                "value": None,
                "unit": "%",
                "formula": "(Net Profit / Shareholders' Equity) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Net Profit", net_profit), ("Shareholders' Equity", equity)] if v is None]
            }

        # Debt-to-Equity Ratio
        if debt is not None and equity is not None and equity != 0:
            val = debt / equity
            results["Debt-to-Equity Ratio"] = {
                "value": val,
                "unit": "x",
                "formula": "Total Borrowings / Shareholders' Equity",
                "inputs": {"Borrowings (Debt)": debt, "Shareholders' Equity": equity},
                "status": "Computed",
                "interpretation": "Financial leverage and structural solvency."
            }
        else:
            results["Debt-to-Equity Ratio"] = {
                "value": None,
                "unit": "x",
                "formula": "Total Borrowings / Shareholders' Equity",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Borrowings (Debt)", debt), ("Shareholders' Equity", equity)] if v is None]
            }

        # Cash-to-Debt Ratio
        if cash is not None and debt is not None and debt != 0:
            val = cash / debt
            results["Cash-to-Debt Ratio"] = {
                "value": val,
                "unit": "x",
                "formula": "Cash and Cash Equivalents / Total Borrowings",
                "inputs": {"Cash": cash, "Debt": debt},
                "status": "Computed",
                "interpretation": "Immediate ability to cover debt obligations with liquid reserves."
            }
        else:
            results["Cash-to-Debt Ratio"] = {
                "value": None,
                "unit": "x",
                "formula": "Cash and Cash Equivalents / Total Borrowings",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Cash and Cash Equivalents", cash), ("Borrowings (Debt)", debt)] if v is None]
            }

        # CapEx to Revenue Ratio
        if capex is not None and rev is not None and rev != 0:
            val = (capex / rev) * 100
            results["CapEx Intensity"] = {
                "value": val,
                "unit": "%",
                "formula": "(Capital Expenditure / Revenue) * 100",
                "inputs": {"CapEx": capex, "Revenue": rev},
                "status": "Computed",
                "interpretation": "Reinvestment rate into physical assets and expansion relative to sales."
            }
        else:
            results["CapEx Intensity"] = {
                "value": None,
                "unit": "%",
                "formula": "(Capital Expenditure / Revenue) * 100",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Capital Expenditure", capex), ("Revenue", rev)] if v is None]
            }

        # Free Cash Flow Estimate (Operating Cash Flow - CapEx)
        if ocf is not None and capex is not None:
            fcf = ocf - capex
            results["Free Cash Flow (FCF)"] = {
                "value": fcf,
                "unit": "Absolute",
                "formula": "Operating Cash Flow - Capital Expenditure",
                "inputs": {"Operating Cash Flow": ocf, "Capital Expenditure": capex},
                "status": "Computed",
                "interpretation": "Cash generated after maintaining/expanding asset base."
            }
        else:
            results["Free Cash Flow (FCF)"] = {
                "value": None,
                "unit": "Absolute",
                "formula": "Operating Cash Flow - Capital Expenditure",
                "status": "Inputs Incomplete",
                "missing": [k for k, v in [("Operating Cash Flow", ocf), ("Capital Expenditure", capex)] if v is None]
            }

        return results
