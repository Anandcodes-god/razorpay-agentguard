from typing import List, Dict, Any
from pydantic import BaseModel
from .transaction import TransactionResponse
from .assessment import AssessmentDetail

class SimulationRequest(BaseModel):
    scenario_id: int

class SimulationResponse(BaseModel):
    scenario_name: str
    description: str
    transaction: TransactionResponse
    assessment: AssessmentDetail
    expected_decision: str

class SimulationAllResponse(BaseModel):
    results: List[SimulationResponse]
    summary: Dict[str, int]
