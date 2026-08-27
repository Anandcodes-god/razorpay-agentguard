from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class IntentContractCreate(BaseModel):
    agent_id: str
    raw_instruction: str
    max_amount: Optional[int] = None
    expires_in_hours: int = 24

class IntentContractResponse(BaseModel):
    id: str
    agent_id: str
    raw_instruction: str
    extracted_parameters: Optional[Dict[str, Any]] = None
    max_amount: Optional[int] = None
    categories: Optional[List[str]] = None
    merchant_constraints: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
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
