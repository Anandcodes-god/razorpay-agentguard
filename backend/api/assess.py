"""
Risk Assessment API - The heart of AgentGuard.

POST /api/assess submits a transaction for risk assessment through
the full agent investigation pipeline.
"""
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.database import get_db
from backend.models import Transaction, RiskAssessment, AuditLog, Agent, IntentContract
from backend.schemas.transaction import TransactionCreate
from backend.agent.nodes import (
    verify_agent_node, check_intent_node, check_signals_node,
    llm_reasoning_node, policy_gate_node, agent_valid_router
)

router = APIRouter(tags=["Risk Assessment"])


async def run_assessment_pipeline(transaction_dict: dict, db: AsyncSession) -> dict:
    """Run the full AgentGuard assessment pipeline on a transaction.
    
    Instead of using LangGraph's ainvoke (which can't easily pass DB sessions),
    we manually orchestrate the node functions in sequence.
    This gives us the same graph structure but with clean session management.
    """
    # Initialize state
    state = {
        "transaction": transaction_dict,
        "_session": db,
        "agent_profile": None,
        "intent_contract": None,
        "intent_deviation": None,
        "transaction_history": None,
        "merchant_check": None,
        "llm_analysis": None,
        "llm_recommendation": None,
        "policy_decision": None,
        "policy_reasons": [],
        "policy_flags": {},
        "intent_deviation_score": 0,
        "agent_trust_score": 0,
        "transaction_risk_score": 0,
        "overall_risk_score": 0,
        "audit_timeline": [],
        "assessment_id": str(uuid.uuid4()),
        "agent_valid": False,
    }

    # Node 1: Verify agent
    update = await verify_agent_node(state)
    state.update(update)

    # Conditional routing: if agent is invalid, skip to policy gate
    route = agent_valid_router(state)
    
    if route == "valid":
        # Node 2: Check intent
        update = await check_intent_node(state)
        state.update(update)

        # Node 3: Check signals
        update = await check_signals_node(state)
        state.update(update)

        # Node 4: LLM reasoning
        update = await llm_reasoning_node(state)
        state.update(update)

    # Node 5: Policy gate (always runs)
    update = await policy_gate_node(state)
    state.update(update)

    return state


@router.post("/assess", summary="Submit a transaction for risk assessment")
async def assess_transaction(transaction_in: TransactionCreate, db: AsyncSession = Depends(get_db)):
    """
    Submit a transaction for risk assessment.
    Runs the full AgentGuard investigation pipeline.
    Returns the complete assessment with audit timeline.
    """
    # 1. Create Transaction record
    tx_id = str(uuid.uuid4())
    transaction = Transaction(
        id=tx_id,
        agent_id=transaction_in.agent_id,
        intent_contract_id=transaction_in.intent_contract_id,
        merchant_name=transaction_in.merchant_name,
        merchant_category=transaction_in.merchant_category,
        amount=transaction_in.amount,
        currency=transaction_in.currency or "INR",
        description=transaction_in.description,
        status="pending",
    )
    db.add(transaction)
    await db.flush()

    # 2. Build transaction dict for the pipeline
    tx_dict = {
        "id": tx_id,
        "agent_id": transaction_in.agent_id,
        "intent_contract_id": transaction_in.intent_contract_id,
        "merchant_name": transaction_in.merchant_name,
        "merchant_category": transaction_in.merchant_category,
        "amount": transaction_in.amount,
        "currency": transaction_in.currency or "INR",
        "description": transaction_in.description,
    }

    # 3. Run the assessment pipeline
    try:
        final_state = await run_assessment_pipeline(tx_dict, db)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Assessment pipeline failed: {str(e)}")

    # 4. Create RiskAssessment record
    assessment_id = final_state.get("assessment_id", str(uuid.uuid4()))
    flags = final_state.get("policy_flags", {})
    reasons = final_state.get("policy_reasons", [])

    assessment = RiskAssessment(
        id=assessment_id,
        transaction_id=tx_id,
        intent_deviation_score=final_state.get("intent_deviation_score", 0),
        agent_trust_score=final_state.get("agent_trust_score", 0),
        transaction_risk_score=final_state.get("transaction_risk_score", 0),
        overall_risk_score=final_state.get("overall_risk_score", 0),
        llm_analysis=final_state.get("llm_analysis"),
        llm_recommendation=final_state.get("llm_recommendation"),
        policy_decision=final_state.get("policy_decision", "BLOCK"),
        policy_reasons=json.dumps(reasons),
        intent_amount_exceeded=flags.get("intent_amount_exceeded", False),
        intent_category_mismatch=flags.get("intent_category_mismatch", False),
        agent_expired=flags.get("agent_expired", False),
        agent_unverified=flags.get("agent_unverified", False),
        velocity_anomaly=flags.get("velocity_anomaly", False),
        time_anomaly=flags.get("time_anomaly", False),
    )
    db.add(assessment)

    # 5. Create AuditLog entries from timeline
    timeline = final_state.get("audit_timeline", [])
    for entry in timeline:
        log = AuditLog(
            id=str(uuid.uuid4()),
            assessment_id=assessment_id,
            step_number=entry.get("step_number", 0),
            event_type=entry.get("event_type", "observe"),
            title=entry.get("title", ""),
            detail=entry.get("detail", ""),
            severity=entry.get("severity", "info"),
        )
        db.add(log)

    # 6. Update transaction status
    decision = final_state.get("policy_decision", "BLOCK")
    transaction.status = decision.lower()
    
    await db.commit()

    # 7. Return response
    return {
        "assessment_id": assessment_id,
        "transaction_id": tx_id,
        "policy_decision": decision,
        "policy_reasons": reasons,
        "scores": {
            "intent_deviation": final_state.get("intent_deviation_score", 0),
            "agent_trust": final_state.get("agent_trust_score", 0),
            "transaction_risk": final_state.get("transaction_risk_score", 0),
            "overall": final_state.get("overall_risk_score", 0),
        },
        "flags": flags,
        "llm_analysis": final_state.get("llm_analysis"),
        "llm_recommendation": final_state.get("llm_recommendation"),
        "timeline": timeline,
        "agent_profile": final_state.get("agent_profile"),
        "intent_contract": final_state.get("intent_contract"),
        "intent_deviation": final_state.get("intent_deviation"),
    }


@router.get("/assessments", summary="List recent assessments")
async def list_assessments(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """List the most recent risk assessments."""
    result = await db.execute(
        select(RiskAssessment)
        .order_by(desc(RiskAssessment.created_at))
        .limit(limit)
    )
    assessments = result.scalars().all()
    return [
        {
            "id": a.id,
            "transaction_id": a.transaction_id,
            "policy_decision": a.policy_decision,
            "overall_risk_score": a.overall_risk_score,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in assessments
    ]


@router.get("/assessments/{assessment_id}", summary="Get full assessment details")
async def get_assessment(assessment_id: str, db: AsyncSession = Depends(get_db)):
    """Get full assessment with timeline."""
    result = await db.execute(
        select(RiskAssessment).filter(RiskAssessment.id == assessment_id)
    )
    assessment = result.scalars().first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    # Fetch timeline
    logs_result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.assessment_id == assessment_id)
        .order_by(AuditLog.step_number)
    )
    logs = logs_result.scalars().all()

    # Fetch transaction
    tx_result = await db.execute(
        select(Transaction).filter(Transaction.id == assessment.transaction_id)
    )
    tx = tx_result.scalars().first()

    return {
        "assessment": {
            "id": assessment.id,
            "transaction_id": assessment.transaction_id,
            "policy_decision": assessment.policy_decision,
            "policy_reasons": json.loads(assessment.policy_reasons) if assessment.policy_reasons else [],
            "scores": {
                "intent_deviation": assessment.intent_deviation_score,
                "agent_trust": assessment.agent_trust_score,
                "transaction_risk": assessment.transaction_risk_score,
                "overall": assessment.overall_risk_score,
            },
            "flags": {
                "intent_amount_exceeded": assessment.intent_amount_exceeded,
                "intent_category_mismatch": assessment.intent_category_mismatch,
                "agent_expired": assessment.agent_expired,
                "agent_unverified": assessment.agent_unverified,
                "velocity_anomaly": assessment.velocity_anomaly,
                "time_anomaly": assessment.time_anomaly,
            },
            "llm_analysis": assessment.llm_analysis,
            "llm_recommendation": assessment.llm_recommendation,
            "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        },
        "transaction": {
            "id": tx.id,
            "agent_id": tx.agent_id,
            "merchant_name": tx.merchant_name,
            "merchant_category": tx.merchant_category,
            "amount": tx.amount,
            "currency": tx.currency,
            "description": tx.description,
            "status": tx.status,
        } if tx else None,
        "timeline": [
            {
                "step_number": log.step_number,
                "event_type": log.event_type,
                "title": log.title,
                "detail": log.detail,
                "severity": log.severity,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in logs
        ],
    }


@router.get("/assessments/{assessment_id}/timeline", summary="Get audit timeline")
async def get_assessment_timeline(assessment_id: str, db: AsyncSession = Depends(get_db)):
    """Get just the investigation audit timeline for an assessment."""
    logs_result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.assessment_id == assessment_id)
        .order_by(AuditLog.step_number)
    )
    logs = logs_result.scalars().all()
    if not logs:
        raise HTTPException(status_code=404, detail="Assessment not found or no timeline")

    return [
        {
            "step_number": log.step_number,
            "event_type": log.event_type,
            "title": log.title,
            "detail": log.detail,
            "severity": log.severity,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in logs
    ]
