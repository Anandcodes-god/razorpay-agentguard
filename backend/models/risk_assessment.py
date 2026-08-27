import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class RiskAssessment(Base):
    __tablename__ = 'risk_assessments'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(String, ForeignKey("transactions.id"), nullable=False)
    intent_deviation_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    agent_trust_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    transaction_risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    overall_risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    llm_analysis: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    llm_recommendation: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    policy_decision: Mapped[str] = mapped_column(String, nullable=False)
    policy_reasons: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    intent_amount_exceeded: Mapped[bool] = mapped_column(Boolean, default=False)
    intent_category_mismatch: Mapped[bool] = mapped_column(Boolean, default=False)
    agent_expired: Mapped[bool] = mapped_column(Boolean, default=False)
    agent_unverified: Mapped[bool] = mapped_column(Boolean, default=False)
    velocity_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    time_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transaction: Mapped["Transaction"] = relationship(back_populates="risk_assessment")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="risk_assessment", cascade="all, delete-orphan")
