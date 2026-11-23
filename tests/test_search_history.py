import pytest
import uuid
from auth.authentication import create_user
from modules.organisation_search import OrganisationSearchEngine
from database.connection import init_db, SessionLocal
from database.models import SearchHistory

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_user_search_history_recording_and_retrieval():
    search_engine = OrganisationSearchEngine()
    
    # 1. Create a user
    email = f"user_{uuid.uuid4().hex[:6]}@domain.edu"
    ok, _, user = create_user(email, "Password123")
    assert ok is True

    # 2. Create a test organisation
    org_candidate = {
        "name": f"Enterprise Test {uuid.uuid4().hex[:4]}",
        "country": "India",
        "industry": "Technology",
        "ticker": "TEST",
        "stock_exchange": "NSE"
    }
    org = search_engine.get_or_create_organisation(org_candidate)
    assert org.id is not None

    # 3. Record search history
    search_engine.record_user_search(user.id, org.id)

    # 4. Retrieve search history
    history = search_engine.get_user_search_history(user.id)
    assert len(history) >= 1
    assert history[0]["org_id"] == org.id
    assert history[0]["name"] == org.name
    assert history[0]["ticker"] == "TEST"
