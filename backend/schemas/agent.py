from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, field_validator, Field

class AgentCreate(BaseModel):
    name: str
    principal_id: str
    
    @field_validator('principal_id')
    @classmethod
    def principal_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('principal_id cannot be empty')
        return v
    scope: Optional[Dict[str, Any]] = None
    max_budget: Optional[int] = Field(default=None, gt=0)
    expires_at: Optional[datetime] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    principal_id: str
    
    @field_validator('principal_id')
    @classmethod
    def principal_id_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('principal_id cannot be empty')
        return v
    is_verified: bool
    scope: Optional[Dict[str, Any]] = None
    max_budget: Optional[int] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Override to parse scope JSON string from DB before validation."""
        import json
        if hasattr(obj, 'scope') and isinstance(obj.scope, str):
            try:
                object.__setattr__(obj, '_scope_parsed', json.loads(obj.scope))
            except (json.JSONDecodeError, TypeError):
                object.__setattr__(obj, '_scope_parsed', None)
            # Create a dict copy with parsed scope
            data = {c.key: getattr(obj, c.key) for c in obj.__table__.columns}
            data['scope'] = getattr(obj, '_scope_parsed', obj.scope)
            return super().model_validate(data, **kwargs)
        return super().model_validate(obj, **kwargs)

class AgentCreateResponse(AgentResponse):
    api_key: str

class AgentTrustScore(BaseModel):
    agent_id: str
    is_verified: bool
    has_principal: bool
    scope_valid: bool
    is_expired: bool
    trust_score: int
