import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class IntentContract(Base):
    __tablename__ = 'intent_contracts'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id: Mapped[str] = mapped_column(String, ForeignKey("agents.id"), nullable=False)
    raw_instruction: Mapped[str] = mapped_column(String, nullable=False)
    purpose: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    categories: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    max_amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String, default="INR")
    merchant_constraints: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    requires_confirmation_above: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    agent: Mapped["Agent"] = relationship(back_populates="intent_contracts")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="intent_contract")
