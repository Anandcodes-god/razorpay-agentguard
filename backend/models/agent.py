import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base

class Agent(Base):
    __tablename__ = 'agents'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    principal_id: Mapped[str] = mapped_column(String, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    scope: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    max_budget: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    intent_contracts: Mapped[List["IntentContract"]] = relationship(back_populates="agent", cascade="all, delete-orphan")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="agent", cascade="all, delete-orphan")
