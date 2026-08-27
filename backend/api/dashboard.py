from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.database import get_db
from backend.models import RiskAssessment, Transaction, Agent

router = APIRouter(tags=["Dashboard"])

@router.get("/stats", summary="Return aggregated dashboard stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Return aggregated statistics for the dashboard."""
    # Count of assessments
    total_assessments = await db.scalar(select(func.count(RiskAssessment.id)))
    allowed = await db.scalar(select(func.count(RiskAssessment.id)).filter(RiskAssessment.policy_decision == "ALLOW"))
    reviewed = await db.scalar(select(func.count(RiskAssessment.id)).filter(RiskAssessment.policy_decision == "REVIEW"))
    blocked = await db.scalar(select(func.count(RiskAssessment.id)).filter(RiskAssessment.policy_decision == "BLOCK"))

    # Sums of transactions
    total_amount = await db.scalar(select(func.sum(Transaction.amount))) or 0.0
    
    allowed_amount = await db.scalar(
        select(func.sum(Transaction.amount))
        .join(RiskAssessment, Transaction.id == RiskAssessment.transaction_id)
        .filter(RiskAssessment.policy_decision == "ALLOW")
    ) or 0.0

    blocked_amount = await db.scalar(
        select(func.sum(Transaction.amount))
        .join(RiskAssessment, Transaction.id == RiskAssessment.transaction_id)
        .filter(RiskAssessment.policy_decision == "BLOCK")
    ) or 0.0

    # Recent assessments
    recent = await db.execute(
        select(RiskAssessment)
        .order_by(desc(RiskAssessment.created_at))
        .limit(10)
    )
    recent_assessments = recent.scalars().all()

    return {
        "total_assessments": total_assessments or 0,
        "allowed": allowed or 0,
        "reviewed": reviewed or 0,
        "blocked": blocked or 0,
        "total_amount_assessed": float(total_amount),
        "total_amount_allowed": float(allowed_amount),
        "total_amount_blocked": float(blocked_amount),
        "recent_assessments": recent_assessments
    }

@router.get("/agents", summary="Return all agents with stats")
async def get_dashboard_agents(db: AsyncSession = Depends(get_db)):
    """Return all agents with their assessment counts."""
    # Simple join to get counts per agent
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    
    data = []
    for agent in agents:
        count = await db.scalar(
            select(func.count(Transaction.id))
            .filter(Transaction.agent_id == agent.id)
        )
        agent_dict = agent.__dict__.copy()
        agent_dict.pop("_sa_instance_state", None)
        agent_dict["assessment_count"] = count or 0
        data.append(agent_dict)

    return data
