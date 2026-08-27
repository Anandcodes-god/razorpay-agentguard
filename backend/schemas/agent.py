from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AgentCreate(BaseModel):
    name: str
    principal_id: str
    is_verified: bool = False
    scope: Optional[Dict[str, Any]] = None
    max_budget: Optional[int] = None
    expires_at: Optional[datetime] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    principal_id: str
    is_verified: bool
    scope: Optional[Dict[str, Any]] = None
    max_budget: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AgentTrustScore(BaseModel):
    agent_id: str
    is_verified: bool
    has_principal: bool
    scope_valid: bool
    is_expired: bool
    trust_score: int
