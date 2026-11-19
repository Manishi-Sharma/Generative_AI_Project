"""
Investment management module.
Provides portfolio allocation analysis, scenario-based returns,
NPV, ROI, compound interest modeling, and portfolio risk evaluation.
"""

from typing import List, Optional, Tuple, Dict, Any
import json
import pandas as pd
from sqlalchemy.orm import Session
from database.models import Investment
from utils.calculations import (
    calculate_simple_interest,
    calculate_compound_interest,
    calculate_roi,
    calculate_npv,
)


def add_investment(
    db: Session,
    org_id: int,
    data: Dict[str, Any]
) -> Tuple[bool, Optional[Investment], str]:
    """Adds a new investment asset to an organisation's portfolio."""
    try:
        cash_flows = data.get("cash_flows", [])
        cash_flows_json = json.dumps(cash_flows) if cash_flows else None

        inv = Investment(
            org_id=org_id,
            name=data["name"].strip(),
            category=data.get("category", "Equities"),
            amount=float(data["amount"]),
            expected_return_rate=float(data["expected_return_rate"]),
            duration_years=int(data.get("duration_years", 3)),
            risk_category=data.get("risk_category", "Moderate"),
            cash_flows_json=cash_flows_json,
            investment_date=str(data.get("investment_date", "2026-01-01")),
            is_active=bool(data.get("is_active", True)),
            notes=data.get("notes", ""),
        )
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return True, inv, "Investment added successfully."
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to record investment: {str(e)}"


def get_investments(db: Session, org_id: int, active_only: bool = True) -> List[Investment]:
    """Retrieve all investments for an organisation."""
    query = db.query(Investment).filter(Investment.org_id == org_id)
    if active_only:
        query = query.filter(Investment.is_active == True)
    return query.order_by(Investment.amount.desc()).all()


def get_investments_dataframe(db: Session, org_id: int) -> pd.DataFrame:
    """Returns investments as an enriched DataFrame with calculated metrics."""
    investments = get_investments(db, org_id, active_only=False)
    if not investments:
        return pd.DataFrame()

    data = []
    for inv in investments:
        simple_interest = calculate_simple_interest(inv.amount, inv.expected_return_rate, inv.duration_years)
        compound_interest = calculate_compound_interest(inv.amount, inv.expected_return_rate, inv.duration_years)
        expected_total = inv.amount + compound_interest
        expected_roi = calculate_roi(expected_total, inv.amount)

        # Parse cash flows for NPV
        cash_flows = []
        if inv.cash_flows_json:
            try:
                cash_flows = json.loads(inv.cash_flows_json)
            except Exception:
                cash_flows = []

        if not cash_flows and inv.duration_years > 0:
            # Generate default annual return cash flow if not explicitly entered
            annual_cash_flow = (compound_interest + inv.amount) / inv.duration_years
            cash_flows = [annual_cash_flow] * inv.duration_years

        # Assume 8% corporate hurdle / discount rate for NPV
        discount_rate = 0.08
        npv_val = calculate_npv(discount_rate, inv.amount, cash_flows)

        data.append({
            "id": inv.id,
            "name": inv.name,
            "category": inv.category,
            "amount": inv.amount,
            "expected_return_rate": inv.expected_return_rate,
            "return_pct_str": f"{inv.expected_return_rate * 100:.1f}%",
            "duration_years": inv.duration_years,
            "risk_category": inv.risk_category,
            "simple_interest": simple_interest,
            "compound_interest": compound_interest,
            "projected_value": expected_total,
            "expected_roi": expected_roi,
            "npv": npv_val,
            "investment_date": inv.investment_date,
            "is_active": inv.is_active,
            "notes": inv.notes or "",
        })
    return pd.DataFrame(data)


def analyze_investment_portfolio(db: Session, org_id: int) -> Dict[str, Any]:
    """Computes comprehensive portfolio allocation, weighted returns, and risk metrics."""
    df = get_investments_dataframe(db, org_id)
    if df.empty:
        return {
            "total_invested": 0.0,
            "weighted_return": 0.0,
            "portfolio_npv": 0.0,
            "risk_distribution": {},
            "category_distribution": {},
            "active_count": 0,
            "scenario_projections": {},
        }

    active_df = df[df["is_active"] == True]
    total_invested = float(active_df["amount"].sum())

    if total_invested > 0:
        weighted_return = float((active_df["amount"] * active_df["expected_return_rate"]).sum() / total_invested)
    else:
        weighted_return = 0.0

    total_npv = float(active_df["npv"].sum())

    risk_dist = active_df.groupby("risk_category")["amount"].sum().to_dict()
    category_dist = active_df.groupby("category")["amount"].sum().to_dict()

    # Scenario-based returns (Bear: -30% performance, Base: 100%, Bull: +35%)
    # Clearly labeled as assumptions
    base_return = float(active_df["compound_interest"].sum())
    scenario_projections = {
        "bear_case": {
            "label": "Pessimistic (-30% Yield Shock)",
            "projected_yield": round(base_return * 0.70, 2),
            "projected_total": round(total_invested + (base_return * 0.70), 2),
        },
        "base_case": {
            "label": "Expected / Baseline Scenario",
            "projected_yield": round(base_return, 2),
            "projected_total": round(total_invested + base_return, 2),
        },
        "bull_case": {
            "label": "Optimistic (+35% Growth Surge)",
            "projected_yield": round(base_return * 1.35, 2),
            "projected_total": round(total_invested + (base_return * 1.35), 2),
        },
    }

    return {
        "total_invested": total_invested,
        "weighted_return": round(weighted_return, 4),
        "portfolio_npv": round(total_npv, 2),
        "risk_distribution": risk_dist,
        "category_distribution": category_dist,
        "active_count": len(active_df),
        "scenario_projections": scenario_projections,
        "disclaimer": "All returns are analytical projections and assumptions, not commercial guarantees.",
    }
