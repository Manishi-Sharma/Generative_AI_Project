"""
Financial data management module.
Handles isolated financial records per organisation, manual entry,
CSV upload processing, calculated financial metrics, and data exports.
"""

from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database.models import FinancialRecord
from utils.calculations import (
    calculate_operating_profit,
    calculate_net_profit,
    calculate_profit_margin,
    calculate_current_ratio,
    calculate_debt_ratio,
)
from utils.validation import validate_financial_csv


def add_financial_record(
    db: Session,
    org_id: int,
    data: Dict[str, Any]
) -> Tuple[bool, Optional[FinancialRecord], str]:
    """Adds a single quarterly/monthly financial record for an organisation."""
    try:
        record = FinancialRecord(
            org_id=org_id,
            year=int(data.get("year", 2026)),
            quarter=int(data.get("quarter", 1)),
            month=int(data.get("month")) if data.get("month") else None,
            revenue=float(data.get("revenue", 0.0)),
            operating_expenses=float(data.get("operating_expenses", 0.0)),
            salaries=float(data.get("salaries", 0.0)),
            production_costs=float(data.get("production_costs", 0.0)),
            electricity=float(data.get("electricity", 0.0)),
            marketing=float(data.get("marketing", 0.0)),
            administration=float(data.get("administration", 0.0)),
            rd_expenses=float(data.get("rd_expenses", 0.0)),
            investments=float(data.get("investments", 0.0)),
            assets=float(data.get("assets", 0.0)),
            liabilities=float(data.get("liabilities", 0.0)),
            cash_reserves=float(data.get("cash_reserves", 0.0)),
            taxes=float(data.get("taxes", 0.0)),
            loan_payments=float(data.get("loan_payments", 0.0)),
            notes=data.get("notes", ""),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return True, record, "Financial record added successfully."
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to add record: {str(e)}"


def get_financial_records(db: Session, org_id: int) -> List[FinancialRecord]:
    """Retrieves all financial records for an organisation sorted chronologically."""
    return db.query(FinancialRecord).filter(
        FinancialRecord.org_id == org_id
    ).order_by(FinancialRecord.year.asc(), FinancialRecord.quarter.asc()).all()


def get_financial_dataframe(db: Session, org_id: int) -> pd.DataFrame:
    """Retrieves records and returns enriched DataFrame with calculated financial ratios."""
    records = get_financial_records(db, org_id)
    if not records:
        return pd.DataFrame()

    data = []
    for r in records:
        op_profit = calculate_operating_profit(r.revenue, r.operating_expenses)
        net_profit = calculate_net_profit(op_profit, r.taxes, r.loan_payments)
        margin = calculate_profit_margin(net_profit, r.revenue)
        curr_ratio = calculate_current_ratio(r.assets, r.liabilities)
        debt_ratio = calculate_debt_ratio(r.liabilities, r.assets)
        cash_flow = round(net_profit + (r.operating_expenses * 0.05), 2)  # Proxy for operational cash flow

        data.append({
            "id": r.id,
            "org_id": r.org_id,
            "year": r.year,
            "quarter": r.quarter,
            "month": r.month,
            "revenue": r.revenue,
            "operating_expenses": r.operating_expenses,
            "salaries": r.salaries,
            "production_costs": r.production_costs,
            "electricity": r.electricity,
            "marketing": r.marketing,
            "administration": r.administration,
            "rd_expenses": r.rd_expenses,
            "investments": r.investments,
            "assets": r.assets,
            "liabilities": r.liabilities,
            "cash_reserves": r.cash_reserves,
            "taxes": r.taxes,
            "loan_payments": r.loan_payments,
            "operating_profit": op_profit,
            "net_profit": net_profit,
            "profit_margin": margin,
            "current_ratio": curr_ratio,
            "debt_ratio": debt_ratio,
            "cash_flow": cash_flow,
            "notes": r.notes or "",
        })
    return pd.DataFrame(data)


def import_financial_csv(
    db: Session,
    org_id: int,
    file_content: Any
) -> Tuple[bool, int, List[str]]:
    """
    Imports and validates financial CSV for a given organisation.
    Enforces tenant data isolation by setting record.org_id explicitly.
    """
    try:
        df = pd.read_csv(file_content)
    except Exception as e:
        return False, 0, [f"Failed to read CSV: {str(e)}"]

    is_valid, clean_df, errors = validate_financial_csv(df)
    if not is_valid:
        return False, 0, errors

    records_added = 0
    try:
        for _, row in clean_df.iterrows():
            record = FinancialRecord(
                org_id=org_id,
                year=int(row["year"]),
                quarter=int(row["quarter"]),
                month=int(row["month"]) if "month" in row and pd.notna(row["month"]) and row["month"] > 0 else None,
                revenue=float(row["revenue"]),
                operating_expenses=float(row["operating_expenses"]),
                salaries=float(row["salaries"]),
                production_costs=float(row["production_costs"]),
                electricity=float(row["electricity"]),
                marketing=float(row["marketing"]),
                administration=float(row["administration"]),
                rd_expenses=float(row["rd_expenses"]),
                investments=float(row["investments"]),
                assets=float(row["assets"]),
                liabilities=float(row["liabilities"]),
                cash_reserves=float(row["cash_reserves"]),
                taxes=float(row["taxes"]),
                loan_payments=float(row["loan_payments"]),
                notes=str(row.get("notes", "CSV Import")),
            )
            db.add(record)
            records_added += 1
        db.commit()
        return True, records_added, []
    except Exception as e:
        db.rollback()
        return False, 0, [f"Database transaction error during import: {str(e)}"]


def get_latest_financial_summary(db: Session, org_id: int) -> Dict[str, Any]:
    """Computes a high-level executive summary of current financial health."""
    df = get_financial_dataframe(db, org_id)
    if df.empty:
        return {
            "has_data": False,
            "total_revenue": 0.0,
            "total_expenses": 0.0,
            "net_profit": 0.0,
            "operating_profit": 0.0,
            "cash_reserves": 0.0,
            "profit_margin": 0.0,
            "current_ratio": 0.0,
            "debt_ratio": 0.0,
            "latest_record": None,
        }

    latest = df.iloc[-1].to_dict()
    total_rev = float(df["revenue"].sum())
    total_exp = float(df["operating_expenses"].sum())
    net_profit = float(df["net_profit"].sum())
    op_profit = float(df["operating_profit"].sum())
    curr_margin = calculate_profit_margin(net_profit, total_rev)

    return {
        "has_data": True,
        "total_revenue": total_rev,
        "total_expenses": total_exp,
        "net_profit": net_profit,
        "operating_profit": op_profit,
        "cash_reserves": float(latest.get("cash_reserves", 0.0)),
        "profit_margin": curr_margin,
        "current_ratio": float(latest.get("current_ratio", 0.0)),
        "debt_ratio": float(latest.get("debt_ratio", 0.0)),
        "latest_record": latest,
    }
