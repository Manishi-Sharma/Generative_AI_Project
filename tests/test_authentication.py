"""
Tests for authentication, password hashing, and role-based access control.
"""

import uuid
import pytest
from database.connection import get_db_context
from database.models import User
from modules.authentication import (
    hash_password,
    verify_password,
    register_user,
    authenticate_user,
    check_permission,
)
import config


def test_password_hashing():
    raw_password = "SecretFinancialPassword123!"
    hashed = hash_password(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_user_registration_and_authentication():
    with get_db_context() as db:
        uid = uuid.uuid4().hex[:8]
        uname = f"testuser_{uid}"
        email = f"{uname}@example.com"
        success, user, msg = register_user(
            db,
            username=uname,
            email=email,
            password="SecurePassword999",
            full_name="Test Financial Analyst",
            role=config.ROLE_FINANCIAL_ANALYST,
        )
        assert success is True
        assert user is not None
        assert user.username == uname

        # Test auth with correct credentials
        auth_success, auth_user, _ = authenticate_user(db, uname, "SecurePassword999")
        assert auth_success is True
        assert auth_user.id == user.id

        # Test auth with wrong credentials
        fail_auth, _, _ = authenticate_user(db, uname, "InvalidPassword")
        assert fail_auth is False


def test_role_permissions():
    # Platform Admin can do everything
    assert check_permission(config.ROLE_PLATFORM_ADMIN, "platform_administration") is True
    assert check_permission(config.ROLE_PLATFORM_ADMIN, "manage_investments") is True

    # Analyst can view but cannot manage org members or platform admin
    assert check_permission(config.ROLE_FINANCIAL_ANALYST, "view_dashboard") is True
    assert check_permission(config.ROLE_FINANCIAL_ANALYST, "manage_org_members") is False
    assert check_permission(config.ROLE_FINANCIAL_ANALYST, "platform_administration") is False
