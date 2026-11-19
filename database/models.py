"""
SQLAlchemy database models for The Financial Butterfly Effect.
Implements multi-tenant schema with isolation by organisation_id,
foreign keys, indices, and audit timestamps.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="financial_analyst", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    memberships: Mapped[List["OrganisationMembership"]] = relationship("OrganisationMembership", back_populates="user", cascade="all, delete-orphan")
    ai_queries: Mapped[List["AIAnalysisHistory"]] = relationship("AIAnalysisHistory", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    org_type: Mapped[str] = mapped_column(String(64), nullable=False)  # Manufacturing, Investment, Education, NGO, etc.
    currency: Mapped[str] = mapped_column(String(8), default="₹", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    annual_budget: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Flags synthetic sample data
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    memberships: Mapped[List["OrganisationMembership"]] = relationship("OrganisationMembership", back_populates="organisation", cascade="all, delete-orphan")
    departments: Mapped[List["Department"]] = relationship("Department", back_populates="organisation", cascade="all, delete-orphan")
    financial_records: Mapped[List["FinancialRecord"]] = relationship("FinancialRecord", back_populates="organisation", cascade="all, delete-orphan")
    investments: Mapped[List["Investment"]] = relationship("Investment", back_populates="organisation", cascade="all, delete-orphan")
    savings_plans: Mapped[List["SavingsPlan"]] = relationship("SavingsPlan", back_populates="organisation", cascade="all, delete-orphan")
    dependencies: Mapped[List["FinancialDependency"]] = relationship("FinancialDependency", back_populates="organisation", cascade="all, delete-orphan")
    scenarios: Mapped[List["Scenario"]] = relationship("Scenario", back_populates="organisation", cascade="all, delete-orphan")
    simulation_results: Mapped[List["SimulationResult"]] = relationship("SimulationResult", back_populates="organisation", cascade="all, delete-orphan")
    risk_reports: Mapped[List["RiskReport"]] = relationship("RiskReport", back_populates="organisation", cascade="all, delete-orphan")
    ai_queries: Mapped[List["AIAnalysisHistory"]] = relationship("AIAnalysisHistory", back_populates="organisation", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Organisation(id={self.id}, name='{self.name}', type='{self.org_type}')>"


class OrganisationMembership(Base):
    __tablename__ = "organisation_memberships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), default="financial_analyst", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="memberships")
    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="memberships")

    __table_args__ = (
        Index("ix_org_membership_user_org", "user_id", "org_id", unique=True),
    )


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    code: Mapped[str] = mapped_column(String(16), nullable=False)
    annual_budget: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    headcount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="departments")
    savings_plans: Mapped[List["SavingsPlan"]] = relationship("SavingsPlan", back_populates="department")


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quarter: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 to 4
    month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 to 12

    # Financial Inflows & Outflows
    revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    operating_expenses: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    salaries: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    production_costs: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    electricity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    marketing: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    administration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rd_expenses: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    investments: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Balance Sheet Items
    assets: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    liabilities: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cash_reserves: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    taxes: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    loan_payments: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="financial_records")

    __table_args__ = (
        Index("ix_org_period", "org_id", "year", "quarter"),
    )


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # Equities, Debt, Infrastructure, R&D, Tech
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    expected_return_rate: Mapped[float] = mapped_column(Float, nullable=False)  # e.g. 0.12 for 12%
    duration_years: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(32), default="Moderate", nullable=False)  # Low, Moderate, High
    cash_flows_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of annual expected flows
    investment_date: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="investments")


class SavingsPlan(Base):
    __tablename__ = "savings_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    target_reduction_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    target_reduction_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reinvestment_pct: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    emergency_reserve_pct: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)
    operational_risk_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="Proposed", nullable=False)  # Proposed, Active, Completed, Cancelled
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="savings_plans")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="savings_plans")


class FinancialDependency(Base):
    __tablename__ = "financial_dependencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node: Mapped[str] = mapped_column(String(64), nullable=False)
    target_node: Mapped[str] = mapped_column(String(64), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)  # Sensitivity coefficient
    lag_periods: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str] = mapped_column(String(256), nullable=False)
    is_positive_relationship: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="dependencies")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(32), default="Custom", nullable=False)  # Optimistic, Baseline, Pessimistic, Custom
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameter_changes_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON dictionary of changes
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="scenarios")
    simulation_results: Mapped[List["SimulationResult"]] = relationship("SimulationResult", back_populates="scenario")


class SimulationResult(Base):
    __tablename__ = "simulation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    scenario_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    simulation_params_json: Mapped[str] = mapped_column(Text, nullable=False)
    results_summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="simulation_results")
    scenario: Mapped[Optional["Scenario"]] = relationship("Scenario", back_populates="simulation_results")


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    overall_risk_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0 to 100
    liquidity_score: Mapped[float] = mapped_column(Float, nullable=False)
    debt_score: Mapped[float] = mapped_column(Float, nullable=False)
    cash_flow_score: Mapped[float] = mapped_column(Float, nullable=False)
    concentration_score: Mapped[float] = mapped_column(Float, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="risk_reports")


class AIAnalysisHistory(Base):
    __tablename__ = "ai_analysis_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str] = mapped_column(String(64), nullable=False)
    was_fallback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    organisation: Mapped["Organisation"] = relationship("Organisation", back_populates="ai_queries")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="ai_queries")
