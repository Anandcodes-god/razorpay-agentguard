import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=False)
    intent_contract_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("intent_contracts.id"), nullable=True)
    razorpay_order_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    merchant_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    merchant_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="INR")
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    agent: Mapped["Agent"] = relationship(back_populates="transactions")
    intent_contract: Mapped[Optional["IntentContract"]] = relationship(back_populates="transactions")
    risk_assessment: Mapped[Optional["RiskAssessment"]] = relationship(back_populates="transaction", uselist=False)
