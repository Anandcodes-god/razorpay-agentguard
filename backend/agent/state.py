from typing import TypedDict, Any
from datetime import datetime

class AgentGuardState(TypedDict, total=False):
    # Input
    transaction: dict                    # The payment request to assess
    _session: Any                        # Database session passed in
    
    # Investigation results (populated by nodes)
    agent_profile: dict | None           # From get_agent_profile tool
    intent_contract: dict | None         # From get_intent_contract tool  
    intent_deviation: dict | None        # From check_intent_deviation tool
    transaction_history: dict | None     # From get_transaction_history tool
    merchant_check: dict | None          # From check_merchant_trust tool
    
    # LLM output
    llm_analysis: str | None             # LLM's investigation narrative
    llm_recommendation: str | None       # LLM's recommendation (ALLOW/REVIEW/BLOCK)
    
    # Policy engine output (this is what actually counts)
    policy_decision: str | None          # ALLOW / REVIEW / BLOCK
    policy_reasons: list[str]            # List of reasons for decision
    policy_flags: dict                   # Boolean flags (intent_amount_exceeded, etc.)
    
    # Scores
    intent_deviation_score: int          # 0-100
    agent_trust_score: int               # 0-100  
    transaction_risk_score: int          # 0-100
    overall_risk_score: int              # 0-100
    
    # Audit
    audit_timeline: list[dict]           # List of audit log entries
    assessment_id: str                   # UUID for this assessment
    
    # Control
    agent_valid: bool                    # Set by verify_agent node
