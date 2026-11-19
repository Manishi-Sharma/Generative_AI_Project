"""
Database initialisation and synthetic sample data seeding.
Seeds three diverse organisations with 12 quarters of realistic historical data,
active investments, departments, savings plans, and scenarios, all clearly labeled as synthetic.
"""

from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from database.connection import init_db, get_db_context
from database.models import (
    User,
    Organisation,
    OrganisationMembership,
    Department,
    FinancialRecord,
    Investment,
    SavingsPlan,
    FinancialDependency,
    Scenario,
)
from modules.authentication import hash_password
from modules.butterfly_engine import DEFAULT_DEPENDENCIES
import config


def seed_database() -> None:
    """Initialises schema and seeds synthetic demonstration data if tables are empty."""
    init_db()

    with get_db_context() as db:
        # Check if already seeded
        if db.query(Organisation).first():
            return

        print("Seeding database with initial admin and synthetic demonstration organisations...")

        # 1. Platform Admin User
        admin_user = User(
            username="admin",
            email="admin@financialbutterfly.local",
            password_hash=hash_password("admin123"),
            full_name="Chief Executive Administrator",
            role=config.ROLE_PLATFORM_ADMIN,
            is_active=True,
        )
        analyst_user = User(
            username="analyst",
            email="analyst@financialbutterfly.local",
            password_hash=hash_password("analyst123"),
            full_name="Lead Financial Analyst",
            role=config.ROLE_FINANCIAL_ANALYST,
            is_active=True,
        )
        db.add_all([admin_user, analyst_user])
        db.flush()

        # 2. Organisation 1: ABC Manufacturing Ltd. (Budget ₹10 Cr = 100,000,000)
        org1 = Organisation(
            name="ABC Manufacturing Ltd.",
            org_type="Manufacturing & Industrial",
            annual_budget=100_000_000.0,
            currency="₹",
            description="Precision automotive components and heavy industrial engineering machinery. (SYNTHETIC DEMO DATA)",
            is_synthetic=True,
        )

        # Organisation 2: XYZ Investment Group (Capital ₹5 Cr = 50,000,000)
        org2 = Organisation(
            name="XYZ Investment Group",
            org_type="Asset Management & Private Equity",
            annual_budget=50_000_000.0,
            currency="₹",
            description="Boutique private equity, venture funding and debt securities asset management firm. (SYNTHETIC DEMO DATA)",
            is_synthetic=True,
        )

        # Organisation 3: Future Education Trust (Budget ₹2 Cr = 20,000,000)
        org3 = Organisation(
            name="Future Education Trust",
            org_type="Non-Profit / Educational Foundation",
            annual_budget=20_000_000.0,
            currency="₹",
            description="Educational foundation delivering STEM laboratories, vocational academies, and merit scholarships. (SYNTHETIC DEMO DATA)",
            is_synthetic=True,
        )

        db.add_all([org1, org2, org3])
        db.flush()

        # Memberships
        for org in [org1, org2, org3]:
            db.add(OrganisationMembership(user_id=admin_user.id, org_id=org.id, role=config.ROLE_ORG_ADMIN))
            db.add(OrganisationMembership(user_id=analyst_user.id, org_id=org.id, role=config.ROLE_FINANCIAL_ANALYST))

        # 3. Departments
        # Org 1: ABC Manufacturing
        d_mfg_prod = Department(org_id=org1.id, name="Plant Operations & Production", code="MFG-PROD", annual_budget=45_000_000.0, headcount=120)
        d_mfg_rd = Department(org_id=org1.id, name="R&D and Product Engineering", code="MFG-RD", annual_budget=15_000_000.0, headcount=25)
        d_mfg_sales = Department(org_id=org1.id, name="Industrial Sales & Marketing", code="MFG-SALES", annual_budget=12_000_000.0, headcount=30)
        d_mfg_admin = Department(org_id=org1.id, name="Executive & Plant Administration", code="MFG-ADMIN", annual_budget=8_000_000.0, headcount=18)

        # Org 2: XYZ Investment
        d_inv_pe = Department(org_id=org2.id, name="Private Equity & Venture Capital", code="INV-PE", annual_budget=25_000_000.0, headcount=12)
        d_inv_debt = Department(org_id=org2.id, name="Structured Debt & Fixed Income", code="INV-DEBT", annual_budget=15_000_000.0, headcount=8)
        d_inv_ops = Department(org_id=org2.id, name="Portfolio Analytics & Compliance", code="INV-OPS", annual_budget=10_000_000.0, headcount=10)

        # Org 3: Future Education Trust
        d_edu_acad = Department(org_id=org3.id, name="Academic Operations & Curriculum", code="EDU-ACAD", annual_budget=10_000_000.0, headcount=45)
        d_edu_infra = Department(org_id=org3.id, name="Campus & Technology Facilities", code="EDU-INFRA", annual_budget=6_000_000.0, headcount=15)
        d_edu_aid = Department(org_id=org3.id, name="Scholarships & Community Outreach", code="EDU-AID", annual_budget=4_000_000.0, headcount=6)

        db.add_all([
            d_mfg_prod, d_mfg_rd, d_mfg_sales, d_mfg_admin,
            d_inv_pe, d_inv_debt, d_inv_ops,
            d_edu_acad, d_edu_infra, d_edu_aid,
        ])
        db.flush()

        # 4. Financial Records (12 Quarters: 2024, 2025, 2026)
        # ABC Manufacturing Ltd: ~₹2.8 Cr - ₹3.4 Cr revenue per quarter
        for year in [2024, 2025, 2026]:
            for qtr in [1, 2, 3, 4]:
                idx = (year - 2024) * 4 + qtr
                growth = 1.0 + (idx * 0.02)
                db.add(FinancialRecord(
                    org_id=org1.id,
                    year=year,
                    quarter=qtr,
                    revenue=round(28_000_000.0 * growth, 2),
                    operating_expenses=round(21_000_000.0 * growth * 0.98, 2),
                    salaries=round(8_500_000.0 * growth, 2),
                    production_costs=round(8_000_000.0 * growth, 2),
                    electricity=round(1_400_000.0 * growth, 2),
                    marketing=round(1_100_000.0 * growth, 2),
                    administration=round(1_000_000.0 * growth, 2),
                    rd_expenses=round(1_000_000.0 * growth, 2),
                    investments=round(3_000_000.0 * growth, 2),
                    assets=round(120_000_000.0 * growth, 2),
                    liabilities=round(35_000_000.0 * (1.0 - (idx * 0.01)), 2),
                    cash_reserves=round(18_000_000.0 * (1.0 + (idx * 0.03)), 2),
                    taxes=round(1_200_000.0 * growth, 2),
                    loan_payments=round(800_000.0, 2),
                    notes=f"Q{qtr} {year} Official Operating Statement (Synthetic)",
                ))

        # XYZ Investment Group: Investment management inflows
        for year in [2024, 2025, 2026]:
            for qtr in [1, 2, 3, 4]:
                idx = (year - 2024) * 4 + qtr
                growth = 1.0 + (idx * 0.025)
                db.add(FinancialRecord(
                    org_id=org2.id,
                    year=year,
                    quarter=qtr,
                    revenue=round(14_000_000.0 * growth, 2),
                    operating_expenses=round(6_500_000.0 * growth, 2),
                    salaries=round(4_000_000.0 * growth, 2),
                    production_costs=200_000.0,
                    electricity=150_000.0,
                    marketing=round(800_000.0 * growth, 2),
                    administration=round(850_000.0 * growth, 2),
                    rd_expenses=round(500_000.0 * growth, 2),
                    investments=round(12_000_000.0 * growth, 2),
                    assets=round(85_000_000.0 * growth, 2),
                    liabilities=round(15_000_000.0, 2),
                    cash_reserves=round(22_000_000.0 * growth, 2),
                    taxes=round(1_500_000.0 * growth, 2),
                    loan_payments=300_000.0,
                    notes=f"Q{qtr} {year} Fund Performance & Yield (Synthetic)",
                ))

        # Future Education Trust: Grants, donations, and tuition
        for year in [2024, 2025, 2026]:
            for qtr in [1, 2, 3, 4]:
                idx = (year - 2024) * 4 + qtr
                growth = 1.0 + (idx * 0.015)
                db.add(FinancialRecord(
                    org_id=org3.id,
                    year=year,
                    quarter=qtr,
                    revenue=round(5_500_000.0 * growth, 2),
                    operating_expenses=round(4_800_000.0 * growth, 2),
                    salaries=round(2_600_000.0 * growth, 2),
                    production_costs=600_000.0,  # Courseware & materials
                    electricity=350_000.0,
                    marketing=300_000.0,
                    administration=450_000.0,
                    rd_expenses=500_000.0,
                    investments=round(1_000_000.0 * growth, 2),
                    assets=round(35_000_000.0 * growth, 2),
                    liabilities=round(6_000_000.0, 2),
                    cash_reserves=round(7_000_000.0 * growth, 2),
                    taxes=100_000.0,
                    loan_payments=150_000.0,
                    notes=f"Q{qtr} {year} Endowment and Operations Ledger (Synthetic)",
                ))

        # 5. Investments
        # ABC Manufacturing Investments
        db.add(Investment(
            org_id=org1.id,
            name="Robotic CNC Automation Line",
            category="Infrastructure & Plant",
            amount=15_000_000.0,
            expected_return_rate=0.14,
            duration_years=4,
            risk_category="Low",
            investment_date="2025-03-15",
            notes="Factory automation project yielding 18% unit cost reduction.",
        ))
        db.add(Investment(
            org_id=org1.id,
            name="EV Component R&D Syndicate",
            category="Research & Development",
            amount=8_000_000.0,
            expected_return_rate=0.22,
            duration_years=5,
            risk_category="High",
            investment_date="2025-07-01",
            notes="Next-gen lightweight aluminium battery casing patent development.",
        ))

        # XYZ Investment Group Investments
        db.add(Investment(
            org_id=org2.id,
            name="Fintech Growth Equity Fund III",
            category="Equities",
            amount=20_000_000.0,
            expected_return_rate=0.18,
            duration_years=5,
            risk_category="Moderate",
            investment_date="2024-11-10",
            notes="Series B/C enterprise payment processing platforms.",
        ))
        db.add(Investment(
            org_id=org2.id,
            name="AAA Corporate Infrastructure Bonds",
            category="Debt & Fixed Income",
            amount=15_000_000.0,
            expected_return_rate=0.085,
            duration_years=3,
            risk_category="Low",
            investment_date="2025-01-20",
            notes="High-grade sovereign-backed debt security portfolio.",
        ))

        # Future Education Trust Investments
        db.add(Investment(
            org_id=org3.id,
            name="Endowment Corpus Liquid Fund",
            category="Fixed Income",
            amount=5_000_000.0,
            expected_return_rate=0.075,
            duration_years=3,
            risk_category="Low",
            investment_date="2024-06-15",
            notes="Perpetual capital pool funding annual student merit scholarships.",
        ))

        # 6. Savings Plans
        db.add(SavingsPlan(
            org_id=org1.id,
            department_id=d_mfg_prod.id,
            name="Industrial Energy & Scrap Reduction Directive",
            target_reduction_pct=6.5,
            target_reduction_amount=2_500_000.0,
            reinvestment_pct=60.0,
            emergency_reserve_pct=40.0,
            operational_risk_score=15.0,
            status="Active",
            notes="Installing power factor controllers and recycling machining swarf.",
        ))
        db.add(SavingsPlan(
            org_id=org2.id,
            department_id=d_inv_ops.id,
            name="Cloud Infrastructure & Vendor License Rationalization",
            target_reduction_pct=10.0,
            target_reduction_amount=1_000_000.0,
            reinvestment_pct=70.0,
            emergency_reserve_pct=30.0,
            operational_risk_score=10.0,
            status="Active",
            notes="Consolidating market data feeds into unified API gateway.",
        ))

        # 7. Financial Dependencies
        for org in [org1, org2, org3]:
            for src, tgt, weight, desc, is_pos in DEFAULT_DEPENDENCIES:
                db.add(FinancialDependency(
                    org_id=org.id,
                    source_node=src,
                    target_node=tgt,
                    weight=weight,
                    lag_periods=1,
                    description=desc,
                    is_positive_relationship=is_pos,
                ))

        # 8. Sample Scenarios
        import json
        db.add(Scenario(
            org_id=org1.id,
            name="2% OPEX Reduction & R&D Reinvestment",
            scenario_type="Optimistic",
            description="Reduce operating costs by 2%, rechanneling 70% of freed cash into automation and engineering.",
            parameter_changes_json=json.dumps({"Operating Expenses": -0.02, "Research and Development": 0.08}),
        ))
        db.add(Scenario(
            org_id=org1.id,
            name="Severe 15% Cost Contraction (Stress Case)",
            scenario_type="Pessimistic",
            description="Deep cost reduction causing secondary productivity erosion and throughput constraints.",
            parameter_changes_json=json.dumps({"Operating Expenses": -0.15, "Marketing": -0.20}),
        ))

        db.commit()
        print("Database initialisation and seeding complete!")


if __name__ == "__main__":
    seed_database()
