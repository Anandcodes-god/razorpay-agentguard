from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from .transaction import TransactionResponse
from .agent import AgentResponse

class AuditLogEntry(BaseModel):
    id: str
    timestamp: datetime
    step_number: int
    event_type: str
    title: str
    detail: str
    severity: str

    model_config = ConfigDict(from_attributes=True)

class AssessmentResponse(BaseModel):
    id: str
    transaction_id: str
    overall_risk_score: int
    agent_trust_score: int
    intent_deviation_score: int
    transaction_risk_score: int
    decision: str
    reasons: List[str]
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AssessmentDetail(AssessmentResponse):
    transaction: TransactionResponse
    agent: AgentResponse
    intent_contract: Optional[Dict[str, Any]] = None
    timeline: List[AuditLogEntry]

class PolicyDecisionResponse(BaseModel):
    decision: str
    reasons: List[str]
    intent_deviation_score: int
    agent_trust_score: int
    transaction_risk_score: int
    overall_risk_score: int
