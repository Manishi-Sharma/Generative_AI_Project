import pytest
from auth.authentication import (
    create_user, authenticate_user, hash_password, verify_password, validate_email_format
)
from database.connection import init_db

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def test_password_hashing():
    raw = "SecurePassword123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_email_validation():
    assert validate_email_format("student@university.edu") is True
    assert validate_email_format("invalid-email") is False
    assert validate_email_format("user@domain") is False

def test_user_registration_and_authentication():
    import uuid
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "MySecretPassword123"

    # Register
    ok, msg, user = create_user(unique_email, pwd, "Test Student")
    assert ok is True
    assert user is not None
    assert user.email == unique_email

    # Duplicate registration should fail
    dup_ok, dup_msg, _ = create_user(unique_email, pwd, "Duplicate")
    assert dup_ok is False
    assert "already exists" in dup_msg

    # Authenticate with correct password
    auth_ok, auth_msg, auth_user = authenticate_user(unique_email, pwd)
    assert auth_ok is True
    assert auth_user.email == unique_email

    # Authenticate with wrong password
    fail_ok, fail_msg, _ = authenticate_user(unique_email, "WrongPass123")
    assert fail_ok is False
