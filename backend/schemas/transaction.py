from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TransactionCreate(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=128)
    intent_contract_id: Optional[str] = None
    merchant_name: str = Field(max_length=255)
    merchant_category: str = Field(max_length=100)
    amount: int = Field(gt=0)
    currency: str = Field(default='INR', max_length=3)
    description: Optional[str] = Field(default=None, max_length=1000)

class TransactionResponse(BaseModel):
    id: str
    agent_id: str
    intent_contract_id: Optional[str] = None
    merchant_name: str
    merchant_category: str
    amount: int
    currency: str = 'INR'
    description: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
