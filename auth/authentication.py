import re
import bcrypt
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import User

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt with salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def validate_email_format(email: str) -> bool:
    """Validates basic email structure."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email.strip()))

def create_user(email: str, password: str, full_name: Optional[str] = None) -> Tuple[bool, str, Optional[User]]:
    """Registers a new user in the database."""
    email = email.strip().lower()
    if not email:
        return False, "Email cannot be empty.", None

    if not validate_email_format(email):
        return False, "Invalid email format.", None

    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    session: Session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            return False, "An account with this email already exists.", None

        pw_hash = hash_password(password)
        new_user = User(
            email=email,
            password_hash=pw_hash,
            full_name=full_name.strip() if full_name else None
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        # Detach/copy necessary attributes
        user_obj = User(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            created_at=new_user.created_at
        )
        return True, "Account created successfully.", user_obj
    except Exception as e:
        session.rollback()
        return False, f"Registration failed: {str(e)}", None
    finally:
        session.close()

def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """Authenticates a user with email and password."""
    email = email.strip().lower()
    if not email or not password:
        return False, "Please provide both email and password.", None

    session: Session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user:
            return False, "Invalid email or password.", None

        if not verify_password(password, user.password_hash):
            return False, "Invalid email or password.", None

        user_obj = User(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
        return True, "Authentication successful.", user_obj
    except Exception as e:
        return False, f"Authentication error: {str(e)}", None
    finally:
        session.close()

def get_user_by_id(user_id: int) -> Optional[User]:
    """Retrieves user by ID."""
    session: Session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            return User(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at
            )
        return None
    finally:
        session.close()
