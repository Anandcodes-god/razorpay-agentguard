"""
Simulation endpoints for running demo scenarios.
"""
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.models import Transaction
from backend.seed.scenarios import get_scenario, get_all_scenarios
from backend.api.assess import run_assessment_pipeline

router = APIRouter(tags=["Simulation"])


async def _inject_velocity_spike(db: AsyncSession, agent_id: str, count: int = 12):
    """Inject rapid transactions to trigger velocity anomaly detection."""
    now = datetime.now(timezone.utc)
    for i in range(count):
        tx = Transaction(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            merchant_name="QuickMart",
            merchant_category="groceries",
            amount=50000 + (i * 1000),  # Varying small amounts
            currency="INR",
            description=f"Rapid transaction {i+1}",
            status="allowed",
            created_at=now - timedelta(minutes=i * 3),  # Spread over last ~36 mins
        )
        db.add(tx)
    await db.flush()


@router.post("/run", summary="Run a single demo scenario")
async def run_scenario(scenario_id: int, db: AsyncSession = Depends(get_db)):
    """Run a specific demo scenario (1-5) through the assessment pipeline."""
    scenario = get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found. Valid: 1-5")

    # Handle special setup for scenario 5 (velocity spike)
    setup = scenario.get("setup", {})
    tx_data = dict(scenario["transaction"])

    if setup.get("inject_velocity_spike"):
        await _inject_velocity_spike(
            db, 
            tx_data["agent_id"], 
            setup.get("spike_count", 12)
        )
        # Override time for scenario 5
        override_hour = setup.get("override_time_hour", 3)
        override_min = setup.get("override_time_minute", 17)
        fake_time = datetime.now(timezone.utc).replace(
            hour=override_hour, minute=override_min
        )
        tx_data["created_at"] = fake_time.isoformat()

    # Run the assessment pipeline
    try:
        result = await run_assessment_pipeline(tx_data, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario {scenario_id} failed: {str(e)}")

    # Persist the results (create Transaction + Assessment + AuditLogs)
    # The pipeline returns state but doesn't persist. We need to persist here.
    import json
    from backend.models import Transaction, RiskAssessment, AuditLog
    
    tx_id = str(uuid.uuid4())
    tx = Transaction(
        id=tx_id,
        agent_id=tx_data["agent_id"],
        intent_contract_id=tx_data.get("intent_contract_id"),
        merchant_name=tx_data.get("merchant_name"),
        merchant_category=tx_data.get("merchant_category"),
        amount=tx_data["amount"],
        currency=tx_data.get("currency", "INR"),
        description=tx_data.get("description"),
        status=result.get("policy_decision", "BLOCK").lower(),
    )
    db.add(tx)

    assessment_id = str(uuid.uuid4())
    flags = result.get("policy_flags", {})
    reasons = result.get("policy_reasons", [])
    assessment = RiskAssessment(
        id=assessment_id,
        transaction_id=tx_id,
        intent_deviation_score=result.get("intent_deviation_score", 0),
        agent_trust_score=result.get("agent_trust_score", 0),
        transaction_risk_score=result.get("transaction_risk_score", 0),
        overall_risk_score=result.get("overall_risk_score", 0),
        llm_analysis=result.get("llm_analysis"),
        llm_recommendation=result.get("llm_recommendation"),
        policy_decision=result.get("policy_decision", "BLOCK"),
        policy_reasons=json.dumps(reasons),
        intent_amount_exceeded=flags.get("intent_amount_exceeded", False),
        intent_category_mismatch=flags.get("intent_category_mismatch", False),
        agent_expired=flags.get("agent_expired", False),
        agent_unverified=flags.get("agent_unverified", False),
        velocity_anomaly=flags.get("velocity_anomaly", False),
        time_anomaly=flags.get("time_anomaly", False),
    )
    db.add(assessment)

    timeline = result.get("audit_timeline", [])
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

    await db.commit()

    return {
        "scenario": {
            "id": scenario["id"],
            "name": scenario["name"],
            "description": scenario["description"],
            "expected_decision": scenario["expected_decision"],
        },
        "actual_decision": result.get("policy_decision"),
        "match": result.get("policy_decision") == scenario["expected_decision"],
        "assessment_id": assessment_id,
        "transaction_id": tx_id,
        "scores": {
            "intent_deviation": result.get("intent_deviation_score", 0),
            "agent_trust": result.get("agent_trust_score", 0),
            "transaction_risk": result.get("transaction_risk_score", 0),
            "overall": result.get("overall_risk_score", 0),
        },
        "policy_reasons": reasons,
        "timeline": timeline,
    }


@router.post("/all", summary="Run all 5 demo scenarios")
async def run_all_scenarios(db: AsyncSession = Depends(get_db)):
    """Run all 5 demo scenarios sequentially and return results."""
    scenarios = get_all_scenarios()
    results = []
    
    for scenario in scenarios:
        try:
            # Reuse the single scenario endpoint logic
            scenario_result = await run_scenario(scenario["id"], db)
            results.append(scenario_result)
        except Exception as e:
            results.append({
                "scenario": {
                    "id": scenario["id"],
                    "name": scenario["name"],
                    "description": scenario["description"],
                    "expected_decision": scenario["expected_decision"],
                },
                "actual_decision": "ERROR",
                "match": False,
                "error": str(e),
            })

    summary = {
        "total": len(results),
        "passed": sum(1 for r in results if r.get("match", False)),
        "failed": sum(1 for r in results if not r.get("match", False)),
        "allowed": sum(1 for r in results if r.get("actual_decision") == "ALLOW"),
        "reviewed": sum(1 for r in results if r.get("actual_decision") == "REVIEW"),
        "blocked": sum(1 for r in results if r.get("actual_decision") == "BLOCK"),
    }

    return {
        "summary": summary,
        "results": results,
    }
