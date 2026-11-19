"""
Database connection and session management for The Financial Butterfly Effect.
Supports SQLite out of the box and maintains PostgreSQL compatibility.
"""

from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL
from database.models import Base

# Engine configuration: SQLite needs check_same_thread=False for Streamlit multi-threading
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)


def init_db() -> None:
    """Create all tables defined in Base models."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for safe database transactions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Session:
    """Returns a standalone session instance; caller must close."""
    return SessionLocal()
