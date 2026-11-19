"""
Tests for multi-tenant organisation isolation.
Ensures strict separation of financial records, investments, and permissions across organisations.
"""

from database.connection import get_db_context
from database.models import Organisation, FinancialRecord, User, OrganisationMembership
from modules.organisation import get_user_organisations
from modules.financial_data import get_financial_records, get_latest_financial_summary
import config


def test_cross_organisation_data_isolation():
    with get_db_context() as db:
        # Fetch ABC Manufacturing and XYZ Investment
        org1 = db.query(Organisation).filter(Organisation.name == "ABC Manufacturing Ltd.").first()
        org2 = db.query(Organisation).filter(Organisation.name == "XYZ Investment Group").first()

        assert org1 is not None
        assert org2 is not None
        assert org1.id != org2.id

        # Retrieve records isolated by org_id
        records_org1 = get_financial_records(db, org1.id)
        records_org2 = get_financial_records(db, org2.id)

        assert len(records_org1) > 0
        assert len(records_org2) > 0

        # Verify no cross-tenant bleeding
        for r in records_org1:
            assert r.org_id == org1.id
            assert r.org_id != org2.id

        for r in records_org2:
            assert r.org_id == org2.id
            assert r.org_id != org1.id

        # Verify executive summary isolation
        sum1 = get_latest_financial_summary(db, org1.id)
        sum2 = get_latest_financial_summary(db, org2.id)

        # Revenue for ABC Manufacturing (~₹2.8-3.4Cr/qtr) vs XYZ (~₹1.4Cr/qtr)
        assert sum1["total_revenue"] != sum2["total_revenue"]


def test_user_tenant_membership_isolation():
    import uuid
    with get_db_context() as db:
        # Create an isolated user who only belongs to Org 3
        org3 = db.query(Organisation).filter(Organisation.name == "Future Education Trust").first()
        assert org3 is not None

        rand_id = uuid.uuid4().hex[:8]
        test_user = User(
            username=f"isolated_edu_{rand_id}",
            email=f"edu_{rand_id}@example.com",
            password_hash="fakehash",
            full_name="Edu Analyst Only",
            role=config.ROLE_FINANCIAL_ANALYST,
            is_active=True,
        )
        db.add(test_user)
        db.flush()

        # Grant membership only to Org 3
        mem = OrganisationMembership(user_id=test_user.id, org_id=org3.id, role=config.ROLE_FINANCIAL_ANALYST)
        db.add(mem)
        db.commit()

        # Query user's accessible orgs
        accessible_orgs = get_user_organisations(db, test_user)
        assert len(accessible_orgs) == 1
        assert accessible_orgs[0].id == org3.id
        assert accessible_orgs[0].name == "Future Education Trust"
