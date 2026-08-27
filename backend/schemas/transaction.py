from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class TransactionCreate(BaseModel):
    agent_id: str
    intent_contract_id: Optional[str] = None
    merchant_name: str
    merchant_category: str
    amount: int
    currency: str = 'INR'
    description: Optional[str] = None

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
