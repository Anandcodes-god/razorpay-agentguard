from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field

class IntentContractCreate(BaseModel):
    agent_id: str
    raw_instruction: str = Field(max_length=2000)
    max_amount: Optional[int] = Field(default=None, gt=0)
    expires_in_hours: int = Field(default=24, ge=1, le=8760)

class IntentContractResponse(BaseModel):
    id: str
    agent_id: str
    raw_instruction: str
    purpose: Optional[str] = None
    categories: Optional[str] = None
    max_amount: int
    currency: str = 'INR'
    merchant_constraints: Optional[str] = None
    requires_confirmation_above: Optional[int] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class IntentDeviationResult(BaseModel):
    amount_deviation_pct: float
    amount_exceeds_max: bool
    category_match: bool
    merchant_allowed: bool
    within_budget: bool
    details: Dict[str, Any]
