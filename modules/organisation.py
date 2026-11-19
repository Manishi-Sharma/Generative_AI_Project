"""
Multi-organisation tenant management and strict data isolation engine.
Guarantees cross-tenant boundaries and enforces role-based membership.
"""

from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from database.models import Organisation, OrganisationMembership, User, Department
import config


def create_organisation(
    db: Session,
    name: str,
    org_type: str,
    annual_budget: float,
    currency: str = "₹",
    description: Optional[str] = None,
    creator_user_id: Optional[int] = None,
    is_synthetic: bool = False,
) -> Tuple[bool, Optional[Organisation], str]:
    """Creates a new organisation and optionally assigns creator as org_admin."""
    existing = db.query(Organisation).filter(Organisation.name == name.strip()).first()
    if existing:
        return False, None, f"Organisation '{name}' already exists."

    org = Organisation(
        name=name.strip(),
        org_type=org_type.strip(),
        annual_budget=float(annual_budget),
        currency=currency,
        description=description.strip() if description else "",
        is_synthetic=is_synthetic,
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Assign membership to creator if specified
    if creator_user_id:
        membership = OrganisationMembership(
            user_id=creator_user_id,
            org_id=org.id,
            role=config.ROLE_ORG_ADMIN,
        )
        db.add(membership)
        db.commit()

    return True, org, "Organisation created successfully."


def get_user_organisations(db: Session, user: User) -> List[Organisation]:
    """
    Returns organisations accessible to the user.
    Platform Admin has universal access; other roles access only their assigned organisations.
    """
    if user.role == config.ROLE_PLATFORM_ADMIN:
        return db.query(Organisation).order_by(Organisation.name).all()

    memberships = db.query(OrganisationMembership).filter(OrganisationMembership.user_id == user.id).all()
    org_ids = [m.org_id for m in memberships]
    if not org_ids:
        return []
    return db.query(Organisation).filter(Organisation.id.in_(org_ids)).order_by(Organisation.name).all()


def get_organisation_by_id(db: Session, org_id: int) -> Optional[Organisation]:
    """Retrieve organisation by ID."""
    return db.query(Organisation).filter(Organisation.id == org_id).first()


def add_user_to_organisation(
    db: Session,
    user_id: int,
    org_id: int,
    role: str = config.ROLE_FINANCIAL_ANALYST
) -> Tuple[bool, str]:
    """Add a user membership to an organisation."""
    existing = db.query(OrganisationMembership).filter(
        OrganisationMembership.user_id == user_id,
        OrganisationMembership.org_id == org_id,
    ).first()

    if existing:
        existing.role = role
        db.commit()
        return True, "User role updated within organisation."

    membership = OrganisationMembership(
        user_id=user_id,
        org_id=org_id,
        role=role,
    )
    db.add(membership)
    db.commit()
    return True, "User added to organisation."


def get_organisation_departments(db: Session, org_id: int) -> List[Department]:
    """List departments belonging to a specific organisation."""
    return db.query(Department).filter(Department.org_id == org_id).all()


def create_department(
    db: Session,
    org_id: int,
    name: str,
    code: str,
    annual_budget: float,
    headcount: int = 1
) -> Department:
    """Create a new department for an organisation."""
    dept = Department(
        org_id=org_id,
        name=name.strip(),
        code=code.strip().upper(),
        annual_budget=float(annual_budget),
        headcount=int(headcount),
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept
