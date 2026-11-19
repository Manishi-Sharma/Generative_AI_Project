"""
Organisation-aware AI Financial Assistant module.
Packages authorized organisation data summaries into high-signal prompts
for NVIDIA Nemotron and records queries in the audit log.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import AIAnalysisHistory, Organisation
from modules.financial_data import get_latest_financial_summary
from modules.investment import analyze_investment_portfolio
from modules.savings import analyze_expense_saving_opportunities
from modules.risk_analysis import evaluate_financial_risks
from modules.nvidia_client import nvidia_client
from utils.calculations import format_currency


def ask_financial_assistant(
    db: Session,
    org_id: int,
    user_id: Optional[int],
    user_query: str,
) -> Dict[str, Any]:
    """
    Answers user financial inquiries with full awareness of the authorized organisation's
    calculated indicators. Strictly isolates data to `org_id`.
    """
    org = db.query(Organisation).filter(Organisation.id == org_id).first()
    org_name = org.name if org else "Target Organisation"
    currency = org.currency if org else "₹"

    # Gather calculated executive metrics
    summary = get_latest_financial_summary(db, org_id)
    inv_analysis = analyze_investment_portfolio(db, org_id)
    savings_analysis = analyze_expense_saving_opportunities(db, org_id)

    # Build concise context block
    context_lines = [
        f"Organisation: {org_name} (Currency: {currency})",
        f"Total Annual Revenue: {format_currency(summary['total_revenue'], currency, abbreviate=True)}",
        f"Total Annual Expenses: {format_currency(summary['total_expenses'], currency, abbreviate=True)}",
        f"Net Profit: {format_currency(summary['net_profit'], currency, abbreviate=True)} (Margin: {summary['profit_margin']:.1f}%)",
        f"Liquid Cash Reserves: {format_currency(summary['cash_reserves'], currency, abbreviate=True)}",
        f"Current Ratio: {summary['current_ratio']:.2f} | Debt Ratio: {summary['debt_ratio']:.2f}",
        f"Total Invested Capital: {format_currency(inv_analysis['total_invested'], currency, abbreviate=True)} across {inv_analysis['active_count']} assets",
        f"Weighted Investment Yield: {inv_analysis['weighted_return'] * 100:.2f}%",
        f"Identified Safe Expense Savings Potential: {format_currency(savings_analysis.get('potential_total_savings', 0.0), currency, abbreviate=True)}",
    ]
    context_str = "\n".join(context_lines)

    system_prompt = (
        "You are an expert Chief Financial Officer and AI Financial Assistant for 'The Financial Butterfly Effect' system. "
        "You provide rigorous, quantitative, and strategic financial advice to corporate decision-makers. "
        "Always base your responses on the calculated figures provided. Emphasize multi-stage interconnected consequences (the butterfly effect), "
        "including both positive benefits and negative trade-offs. Never invent unsubstantiated numbers. Keep your advice structured, "
        "actionable, and mathematically sound."
    )

    full_user_prompt = f"""
Financial Context of Authorized Organisation:
{context_str}

User Question:
{user_query}

Provide a comprehensive, professional response addressing the user's specific scenario.
"""

    result = nvidia_client.query(system_prompt, full_user_prompt)

    # Record interaction in database for audit trail
    try:
        history_entry = AIAnalysisHistory(
            org_id=org_id,
            user_id=user_id,
            prompt=user_query,
            response=result["response"],
            model_used=result["model"],
            was_fallback=result["was_fallback"],
            timestamp=datetime.utcnow(),
        )
        db.add(history_entry)
        db.commit()
    except Exception:
        db.rollback()

    return result


def get_ai_history(db: Session, org_id: int, limit: int = 20) -> List[AIAnalysisHistory]:
    """Retrieve audit history of AI queries for the organisation."""
    return db.query(AIAnalysisHistory).filter(
        AIAnalysisHistory.org_id == org_id
    ).order_by(AIAnalysisHistory.timestamp.desc()).limit(limit).all()
