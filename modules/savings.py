"""
Savings optimization and expense reduction module.
Models cost rationalization, savings reallocation into emergency reserves and R&D,
while explicitly evaluating operational hazards of excessive budget cuts.
"""

from typing import List, Optional, Tuple, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from database.models import SavingsPlan, Department, FinancialRecord
from modules.financial_data import get_financial_records


def create_savings_plan(
    db: Session,
    org_id: int,
    name: str,
    department_id: Optional[int],
    target_reduction_pct: float,
    target_reduction_amount: float,
    reinvestment_pct: float = 50.0,
    emergency_reserve_pct: float = 50.0,
    notes: str = ""
) -> Tuple[bool, Optional[SavingsPlan], str]:
    """
    Creates an actionable savings proposal.
    Computes operational risk penalty if cuts exceed safe thresholds.
    """
    try:
        # Calculate operational risk: severe cuts (>15%) in key functions damage capacity
        risk_score = 0.0
        if target_reduction_pct > 25.0:
            risk_score = 85.0
        elif target_reduction_pct > 15.0:
            risk_score = 55.0
        elif target_reduction_pct > 8.0:
            risk_score = 25.0
        else:
            risk_score = 10.0

        plan = SavingsPlan(
            org_id=org_id,
            department_id=department_id,
            name=name.strip(),
            target_reduction_pct=float(target_reduction_pct),
            target_reduction_amount=float(target_reduction_amount),
            reinvestment_pct=float(reinvestment_pct),
            emergency_reserve_pct=float(emergency_reserve_pct),
            operational_risk_score=risk_score,
            status="Proposed",
            notes=notes.strip(),
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return True, plan, "Savings plan registered."
    except Exception as e:
        db.rollback()
        return False, None, f"Failed to save plan: {str(e)}"


def get_savings_plans(db: Session, org_id: int) -> List[SavingsPlan]:
    """Retrieve all savings plans for an organisation."""
    return db.query(SavingsPlan).filter(SavingsPlan.org_id == org_id).all()


def analyze_expense_saving_opportunities(db: Session, org_id: int) -> Dict[str, Any]:
    """
    Analyses historical operating expenses across categories,
    pinpointing high-cost drivers and safe reduction targets.
    """
    records = get_financial_records(db, org_id)
    if not records:
        return {
            "has_data": False,
            "annual_operating_expenses": 0.0,
            "category_shares": {},
            "recommendations": [],
        }

    # Aggregate latest 4 quarters (representing 1 fiscal year)
    recent = records[-4:] if len(records) >= 4 else records
    
    salaries = sum(r.salaries for r in recent)
    production = sum(r.production_costs for r in recent)
    electricity = sum(r.electricity for r in recent)
    marketing = sum(r.marketing for r in recent)
    admin = sum(r.administration for r in recent)
    rd = sum(r.rd_expenses for r in recent)
    total_opex = sum(r.operating_expenses for r in recent)

    if total_opex == 0:
        total_opex = salaries + production + electricity + marketing + admin + rd

    categories = {
        "Salaries & Workforce": salaries,
        "Production Costs": production,
        "Administration & Overhead": admin,
        "Marketing & Sales": marketing,
        "Electricity & Utilities": electricity,
        "Research & Development": rd,
    }

    shares = {}
    recommendations = []

    for cat_name, amount in categories.items():
        pct = (amount / total_opex * 100) if total_opex > 0 else 0
        shares[cat_name] = {"amount": amount, "share_pct": round(pct, 2)}

        # Strategic recommendation rules
        if cat_name == "Administration & Overhead" and pct > 12:
            recommendations.append({
                "category": cat_name,
                "urgency": "High",
                "recommended_cut_pct": 10.0,
                "potential_annual_savings": round(amount * 0.10, 2),
                "rationale": "Overhead exceeds 12% benchmark. Streamlining non-core admin preserves operational capabilities.",
                "operational_risk": "Low - minimal impact on core output."
            })
        elif cat_name == "Electricity & Utilities" and pct > 8:
            recommendations.append({
                "category": cat_name,
                "urgency": "Medium",
                "recommended_cut_pct": 12.0,
                "potential_annual_savings": round(amount * 0.12, 2),
                "rationale": "Energy optimization (solar transition, power-factor audits) can yield double-digit cost reduction.",
                "operational_risk": "Negligible - technology efficiency improvement."
            })
        elif cat_name == "Marketing & Sales" and pct > 20:
            recommendations.append({
                "category": cat_name,
                "urgency": "Medium",
                "recommended_cut_pct": 8.0,
                "potential_annual_savings": round(amount * 0.08, 2),
                "rationale": "Refocus ad spend onto highest-converting channels; trim bottom 20% unprofitable campaigns.",
                "operational_risk": "Moderate - monitor lead pipeline closely to avoid revenue compression."
            })

    # Total potential savings across all recommended safe cuts
    potential_total_savings = sum(r["potential_annual_savings"] for r in recommendations)

    return {
        "has_data": True,
        "annual_operating_expenses": total_opex,
        "category_shares": shares,
        "recommendations": recommendations,
        "potential_total_savings": potential_total_savings,
    }


def simulate_savings_reinvestment(
    annual_savings: float,
    reinvestment_pct: float = 60.0,
    emergency_reserve_pct: float = 40.0,
    years: int = 5,
    reinvestment_roi_rate: float = 0.12,
    reserve_interest_rate: float = 0.06
) -> pd.DataFrame:
    """
    Simulates multi-year accumulation of saved capital divided between
    productive reinvestment and compounding liquid emergency reserves.
    """
    records = []
    cum_reinvested = 0.0
    cum_reserves = 0.0
    cum_returns = 0.0

    reinvest_annual = annual_savings * (reinvestment_pct / 100.0)
    reserve_annual = annual_savings * (emergency_reserve_pct / 100.0)

    for year in range(1, years + 1):
        # Emergency reserve grows with interest + new annual contribution
        cum_reserves = (cum_reserves * (1.0 + reserve_interest_rate)) + reserve_annual
        
        # Productive capital creates additional annual cash returns
        annual_yield = cum_reinvested * reinvestment_roi_rate
        cum_returns += annual_yield
        cum_reinvested += reinvest_annual

        total_value_created = cum_reserves + cum_reinvested + cum_returns

        records.append({
            "Year": f"Year {year}",
            "Annual Savings": annual_savings,
            "Reinvested Capital": round(cum_reinvested, 2),
            "Emergency Reserves": round(cum_reserves, 2),
            "Cumulative Returns": round(cum_returns, 2),
            "Total Value Created": round(total_value_created, 2),
        })

    return pd.DataFrame(records)
