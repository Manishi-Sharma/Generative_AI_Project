from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenarios = relationship("Scenario", back_populates="user", cascade="all, delete-orphan")
    ai_reports = relationship("AIReport", back_populates="user", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan", order_by="desc(SearchHistory.searched_at)")

class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    country = Column(String(100), nullable=True)
    industry = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    stock_exchange = Column(String(100), nullable=True)
    ticker = Column(String(50), nullable=True)
    is_listed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    financial_records = relationship("FinancialData", back_populates="organisation", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="organisation", cascade="all, delete-orphan")
    ai_reports = relationship("AIReport", back_populates="organisation", cascade="all, delete-orphan")
    search_history = relationship("SearchHistory", back_populates="organisation", cascade="all, delete-orphan")

class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String(150), index=True, nullable=False)
    value = Column(Float, nullable=True)  # None if unavailable
    currency = Column(String(20), default="USD")
    unit = Column(String(50), default="Absolute")  # e.g., Billions, Millions, Absolute, %
    period = Column(String(100), nullable=True)  # e.g., FY2023, Q3 2024
    source_name = Column(String(255), nullable=True)
    source_url = Column(String(1024), nullable=True)
    status = Column(String(100), nullable=False)  # PUBLIC INFORMATION FOUND, NOT PUBLICLY AVAILABLE, etc.
    is_calculated = Column(Boolean, default=False)
    publication_date = Column(String(100), nullable=True)
    extraction_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    organisation = relationship("Organisation", back_populates="financial_records")

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    variable_name = Column(String(100), nullable=False)
    change_pct = Column(Float, nullable=False)
    time_horizon = Column(String(50), default="1 Year")
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scenarios")
    organisation = relationship("Organisation", back_populates="scenarios")
    simulation_results = relationship("SimulationResult", back_populates="scenario", cascade="all, delete-orphan")
    ai_reports = relationship("AIReport", back_populates="scenario", cascade="all, delete-orphan")

class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    step = Column(Integer, default=0)  # 0: initial, 1: direct, 2: second-order, etc.
    variable_name = Column(String(100), nullable=False)
    baseline_value = Column(Float, nullable=True)
    simulated_value = Column(Float, nullable=True)
    delta_pct = Column(Float, nullable=False)
    rationale = Column(Text, nullable=True)

    scenario = relationship("Scenario", back_populates="simulation_results")

class AIReport(Base):
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scenario = relationship("Scenario", back_populates="ai_reports")
    user = relationship("User", back_populates="ai_reports")
    organisation = relationship("Organisation", back_populates="ai_reports")

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    org_id = Column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False)
    searched_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="search_history")
    organisation = relationship("Organisation", back_populates="search_history")
