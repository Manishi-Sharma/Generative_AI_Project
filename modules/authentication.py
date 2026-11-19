"""
Authentication, password hashing, and Role-Based Access Control (RBAC).
Uses bcrypt for cryptographic security and enforces least-privilege role boundaries.
"""

from typing import Optional, Dict, Any, Tuple
import bcrypt
from sqlalchemy.orm import Session
from database.models import User, OrganisationMembership
import config


def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str,
    role: str = config.ROLE_FINANCIAL_ANALYST,
) -> Tuple[bool, Optional[User], str]:
    """Registers a new user into the database."""
    # Check existing user
    existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        if existing_user.username == username:
            return False, None, f"Username '{username}' already exists."
        return False, None, f"Email '{email}' is already registered."

    hashed = hash_password(password)
    user = User(
        username=username.strip(),
        email=email.strip().lower(),
        password_hash=hashed,
        full_name=full_name.strip(),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return True, user, "Registration successful."


def authenticate_user(
    db: Session,
    username_or_email: str,
    password: str
) -> Tuple[bool, Optional[User], str]:
    """Authenticates a user by username or email and verifies password."""
    query = username_or_email.strip()
    user = db.query(User).filter(
        (User.username == query) | (User.email == query.lower())
    ).first()

    if not user:
        return False, None, "Invalid username or password."

    if not user.is_active:
        return False, None, "Account is disabled. Contact system administrator."

    if not verify_password(password, user.password_hash):
        return False, None, "Invalid username or password."

    return True, user, "Authentication successful."


def check_permission(user_role: str, action: str) -> bool:
    """
    Evaluates whether a user role has permission for a specific action.
    Hierarchy:
    platform_admin > org_admin > financial_manager > financial_analyst
    """
    role_hierarchy = {
        config.ROLE_PLATFORM_ADMIN: 4,
        config.ROLE_ORG_ADMIN: 3,
        config.ROLE_FINANCIAL_MANAGER: 2,
        config.ROLE_FINANCIAL_ANALYST: 1,
    }

    action_requirements = {
        "view_dashboard": 1,
        "view_financial_data": 1,
        "run_simulations": 1,
        "export_reports": 1,
        "ask_ai": 1,
        "add_financial_record": 2,
        "upload_csv": 2,
        "manage_investments": 2,
        "manage_savings_plans": 2,
        "manage_scenarios": 2,
        "manage_org_profile": 3,
        "manage_departments": 3,
        "manage_org_members": 3,
        "platform_administration": 4,
    }

    user_level = role_hierarchy.get(user_role, 0)
    required_level = action_requirements.get(action, 4)
    return user_level >= required_level
