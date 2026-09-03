"""
Agent graph node functions for the AgentGuard investigation pipeline.

Each node takes AgentGuardState, performs investigation work, and returns
a partial state update. Audit timeline entries are appended to the state
(not written to DB directly - the API route persists them after completion).
"""
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from backend.agent.state import AgentGuardState
from backend.agent.tools import (
    get_agent_profile, get_intent_contract, check_intent_deviation,
    get_transaction_history, check_merchant_trust, compute_agent_trust_score,
    compute_overall_risk_score
)
from backend.agent.prompts import RISK_ANALYSIS_PROMPT
from backend.policy.engine import PolicyGate

IST = ZoneInfo("Asia/Kolkata")


def _format_rupees(paise: int) -> str:
    """Format paise to rupees string."""
    return f"\u20b9{paise / 100:,.2f}"


def _audit_entry(step: int, event_type: str, title: str, detail: str,
                 severity: str = "info") -> dict:
    """Create an audit timeline entry matching the AuditLog model schema."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step_number": step,
        "event_type": event_type,
        "title": title,
        "detail": detail,
        "severity": severity,
    }


async def verify_agent_node(state: AgentGuardState) -> dict:
    """Node 1: Verify agent identity and compute trust score."""
    session = state.get("_session")
    transaction = state.get("transaction", {})
    agent_id = transaction.get("agent_id", "")
    timeline = list(state.get("audit_timeline", []))
    step = len(timeline) + 1

    if not agent_id:
        timeline.append(_audit_entry(
            step, "observe", "Agent identity check",
            "No agent_id provided in transaction.", "critical"
        ))
        return {
            "agent_profile": {},
            "agent_valid": False,
            "agent_trust_score": 0,
            "audit_timeline": timeline,
        }

    profile = await get_agent_profile(session, agent_id)

    if not profile:
        timeline.append(_audit_entry(
            step, "observe", "Agent identity check",
            f"Agent '{agent_id}' not found in registry.", "critical"
        ))
        return {
            "agent_profile": {},
            "agent_valid": False,
            "agent_trust_score": 0,
            "audit_timeline": timeline,
        }

    trust_score = compute_agent_trust_score(profile)

    # Log identity verification
    if profile.get("is_verified"):
        timeline.append(_audit_entry(
            step, "check", "Agent identity verified",
            f"{profile['name']} | Verified | Principal: {profile.get('principal_id', 'N/A')}",
            "info"
        ))
    else:
        timeline.append(_audit_entry(
            step, "check", "Agent identity check FAILED",
            f"Agent '{profile.get('name', agent_id)}' is NOT verified.",
            "critical"
        ))

    step += 1

    # Check principal binding
    if not profile.get("principal_id"):
        timeline.append(_audit_entry(
            step, "check", "No human principal bound",
            "This agent has no verified human principal.", "critical"
        ))
    step += 1

    # Check expiry
    if profile.get("is_expired"):
        timeline.append(_audit_entry(
            step, "check", "Agent authorization expired",
            f"Authorization expired at {profile.get('expires_at', 'unknown')}.",
            "critical"
        ))
    else:
        timeline.append(_audit_entry(
            step, "check", "Agent authorization active",
            f"Expires: {profile.get('expires_at', 'no expiry set')}",
            "info"
        ))

    # Determine validity: verified + has principal + not expired
    is_valid = (
        profile.get("is_verified", False)
        and bool(profile.get("principal_id"))
        and not profile.get("is_expired", True)
    )

    return {
        "agent_profile": profile,
        "agent_trust_score": trust_score,
        "agent_valid": is_valid,
        "audit_timeline": timeline,
    }


async def check_intent_node(state: AgentGuardState) -> dict:
    """Node 2: Check intent contract and compute deviation."""
    session = state.get("_session")
    transaction = state.get("transaction", {})
    contract_id = transaction.get("intent_contract_id")
    timeline = list(state.get("audit_timeline", []))
    step = len(timeline) + 1

    if not contract_id:
        timeline.append(_audit_entry(
            step, "observe", "Intent contract check",
            "No intent contract associated with this transaction.", "warning"
        ))
        return {
            "intent_contract": None,
            "intent_deviation": None,
            "intent_deviation_score": 50,
            "audit_timeline": timeline,
        }

    contract = await get_intent_contract(session, contract_id)

    if not contract:
        timeline.append(_audit_entry(
            step, "observe", "Intent contract not found",
            f"Contract '{contract_id}' not found in database.", "warning"
        ))
        return {
            "intent_contract": None,
            "intent_deviation": None,
            "intent_deviation_score": 50,
            "audit_timeline": timeline,
        }

    # Log contract loaded
    categories = contract.get("categories", [])
    timeline.append(_audit_entry(
        step, "observe", "Intent contract loaded",
        f"Purpose: {contract.get('purpose', 'N/A')} | Max: {_format_rupees(contract.get('max_amount', 0))} | Categories: {categories}",
        "info"
    ))
    step += 1

    # Check deviation
    deviation = check_intent_deviation(transaction, contract)

    # Log amount check
    tx_amount = transaction.get("amount", 0)
    max_amount = contract.get("max_amount", 0)
    if deviation.get("amount_exceeds_max"):
        pct = deviation.get("amount_deviation_pct", 0)
        timeline.append(_audit_entry(
            step, "check", "AMOUNT EXCEEDS INTENT MAXIMUM",
            f"{_format_rupees(tx_amount)} vs max {_format_rupees(max_amount)} (+{pct:.1f}%)",
            "critical"
        ))
    else:
        usage = deviation.get("budget_usage_pct", 0)
        timeline.append(_audit_entry(
            step, "check", "Amount within budget",
            f"{_format_rupees(tx_amount)} within max {_format_rupees(max_amount)} ({usage:.1f}% used)",
            "info"
        ))
    step += 1

    # Log category check
    if not deviation.get("category_match") and categories:
        tx_cat = transaction.get("merchant_category", "unknown")
        timeline.append(_audit_entry(
            step, "check", "Category mismatch detected",
            f"Transaction category '{tx_cat}' NOT in intent categories: {categories}",
            "warning"
        ))
    elif categories:
        timeline.append(_audit_entry(
            step, "check", "Category matches intent",
            f"'{transaction.get('merchant_category', 'N/A')}' is in allowed categories",
            "info"
        ))

    # Compute score: 100 = perfect match, 0 = max deviation
    dev_pct = deviation.get("amount_deviation_pct", 0)
    dev_score = max(0, int(100 / (1 + dev_pct / 100)))

    return {
        "intent_contract": contract,
        "intent_deviation": deviation,
        "intent_deviation_score": dev_score,
        "audit_timeline": timeline,
    }


async def check_signals_node(state: AgentGuardState) -> dict:
    """Node 3: Check transaction signals - velocity, time, merchant trust."""
    session = state.get("_session")
    transaction = state.get("transaction", {})
    agent_id = transaction.get("agent_id", "")
    merchant_name = transaction.get("merchant_name", "")
    merchant_category = transaction.get("merchant_category", "")
    timeline = list(state.get("audit_timeline", []))
    step = len(timeline) + 1

    # Transaction history / velocity
    tx_history = await get_transaction_history(session, agent_id)

    velocity_ratio = tx_history.get("velocity_ratio", 0)
    recent_count = tx_history.get("recent_1h_count", 0)
    if velocity_ratio > 3.0:
        timeline.append(_audit_entry(
            step, "check", "Velocity anomaly detected",
            f"{recent_count} transactions in last hour ({velocity_ratio:.1f}x above normal)",
            "warning"
        ))
    else:
        timeline.append(_audit_entry(
            step, "check", "Transaction velocity normal",
            f"{tx_history.get('total_count', 0)} transactions in 24h, {recent_count} in last hour",
            "info"
        ))
    step += 1

    # Merchant trust
    merchant_check = check_merchant_trust(merchant_name, merchant_category)
    trust_level = merchant_check.get("trust_level", "unknown")
    trust_score = merchant_check.get("trust_score", 50)
    timeline.append(_audit_entry(
        step, "check",
        f"Merchant: {merchant_name}",
        f"Trust: {trust_level} ({trust_score}/100) | Category verified: {merchant_check.get('category_verified', False)}",
        "info" if trust_level in ("high", "medium") else "warning"
    ))
    step += 1

    # Time-of-day check
    created_at = transaction.get("created_at")
    if not created_at:
        created_at_dt = datetime.now(IST)
    elif isinstance(created_at, str):
        try:
            created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(IST)
        except (ValueError, TypeError):
            created_at_dt = datetime.now(IST)
    else:
        created_at_dt = (created_at.replace(tzinfo=timezone.utc)
                         if created_at.tzinfo is None else created_at).astimezone(IST)
        
    hour = created_at_dt.hour
    if hour < 6 or hour >= 23:
        timeline.append(_audit_entry(
            step, "check", "Unusual transaction time",
            f"Transaction at {created_at_dt.strftime('%H:%M IST')} (outside 6am-11pm window)",
            "warning"
        ))

    # Compute transaction risk score
    tx_risk_score = trust_score
    if velocity_ratio > 3.0:
        tx_risk_score = max(0, tx_risk_score - 30)

    return {
        "transaction_history": tx_history,
        "merchant_check": merchant_check,
        "transaction_risk_score": tx_risk_score,
        "audit_timeline": timeline,
    }


async def llm_reasoning_node(state: AgentGuardState) -> dict:
    """Node 4: LLM risk analysis.

    Gathers all evidence collected so far, sends it to the LLM for analysis,
    and records the LLM's investigation narrative and recommendation.
    Falls back gracefully if the LLM is unavailable.
    """
    timeline = list(state.get("audit_timeline", []))
    step = len(timeline) + 1

    # Build context from gathered evidence
    context = {
        "agent_profile": state.get("agent_profile", {}),
        "intent_contract": state.get("intent_contract"),
        "intent_deviation": state.get("intent_deviation"),
        "transaction": state.get("transaction", {}),
        "transaction_history": state.get("transaction_history"),
        "merchant_check": state.get("merchant_check"),
        "agent_trust_score": state.get("agent_trust_score", 0),
        "intent_deviation_score": state.get("intent_deviation_score", 0),
        "transaction_risk_score": state.get("transaction_risk_score", 0),
    }

    try:
        from backend.services.llm_client import get_llm_client
        llm = get_llm_client()
        result = await llm.analyze_risk(context, RISK_ANALYSIS_PROMPT)

        # Try to parse JSON response
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                analysis = parsed.get("analysis", result)
                recommendation = parsed.get("recommendation", "REVIEW")
            except json.JSONDecodeError:
                analysis = result
                recommendation = "REVIEW"
        else:
            analysis = str(result)
            recommendation = "REVIEW"

        timeline.append(_audit_entry(
            step, "reason", "LLM risk analysis",
            analysis, "info"
        ))

        return {
            "llm_analysis": analysis,
            "llm_recommendation": recommendation,
            "audit_timeline": timeline,
        }

    except Exception as e:
        # Graceful degradation - policy engine will still make the decision
        fallback = (
            "LLM analysis unavailable. Relying on deterministic policy engine only. "
            f"Error: {str(e)}"
        )
        timeline.append(_audit_entry(
            step, "reason", "LLM analysis (fallback)",
            fallback, "warning"
        ))
        return {
            "llm_analysis": fallback,
            "llm_recommendation": "REVIEW",
            "audit_timeline": timeline,
        }


async def policy_gate_node(state: AgentGuardState) -> dict:
    """Node 5: Deterministic policy decision using the full PolicyGate engine.

    This is the node that makes the ACTUAL authorization decision.
    The LLM's recommendation is informational only.
    """
    timeline = list(state.get("audit_timeline", []))
    step = len(timeline) + 1

    # Prepare data for policy engine
    agent_data = state.get("agent_profile", {})
    transaction_data = state.get("transaction", {})
    intent_contract = state.get("intent_contract")

    # Map fields for the policy engine
    policy_transaction = {
        "amount": transaction_data.get("amount", 0),
        "category": transaction_data.get("merchant_category", ""),
        "merchant_name": transaction_data.get("merchant_name", ""),
        "created_at": transaction_data.get("created_at"),
    }

    policy_intent = None
    if intent_contract:
        policy_intent = {
            "max_amount": intent_contract.get("max_amount", 0),
            "allowed_categories": intent_contract.get("categories", []),
            "merchant_constraints": intent_contract.get("merchant_constraints", {}),
            "confirmation_threshold": intent_contract.get("requires_confirmation_above"),
        }

    policy_history = None
    tx_history = state.get("transaction_history")
    if tx_history:
        policy_history = {
            "recent_count": tx_history.get("recent_1h_count", 0),
            "normal_hourly_rate": tx_history.get("normal_hourly_rate", 0),
        }

    # Run the deterministic policy gate
    gate = PolicyGate()
    result = gate.evaluate(agent_data, policy_transaction, policy_intent, policy_history)

    # Compute overall risk score
    overall_score = compute_overall_risk_score(
        state.get("intent_deviation_score", 0),
        state.get("agent_trust_score", 0),
        state.get("transaction_risk_score", 0),
    )
    # Force the visual score to reflect a hard block
    if result.decision == "BLOCK":
        overall_score = min(overall_score, 10)

    # Determine severity for audit log
    if result.decision == "BLOCK":
        severity = "critical"
    elif result.decision == "REVIEW":
        severity = "warning"
    else:
        severity = "info"

    # Log decision
    decision_detail = f"Decision: {result.decision}"
    if result.reasons:
        decision_detail += f" | Reasons: {'; '.join(result.reasons)}"
    decision_detail += f" | Overall safety score: {overall_score}/100"

    timeline.append(_audit_entry(
        step, "decide",
        f"Policy Gate: {result.decision}",
        decision_detail,
        severity
    ))

    # Map policy flags to the RiskAssessment boolean fields
    flags = {
        "intent_amount_exceeded": result.flags.get("intent_amount_exceeded", False),
        "intent_category_mismatch": result.flags.get("category_mismatch", False),
        "agent_expired": result.flags.get("agent_expired", False),
        "agent_unverified": result.flags.get("agent_unverified", False),
        "velocity_anomaly": result.flags.get("high_velocity", False),
        "time_anomaly": result.flags.get("unusual_time", False),
    }

    return {
        "policy_decision": result.decision,
        "policy_reasons": result.reasons,
        "policy_flags": flags,
        "overall_risk_score": overall_score,
        "audit_timeline": timeline,
    }


def agent_valid_router(state: AgentGuardState) -> str:
    """Conditional router after verify_agent.
    If agent_valid is True -> 'valid' (continue investigation)
    If agent_valid is False -> 'invalid' (skip to policy gate for BLOCK)
    """
    if state.get("agent_valid", False):
        return "valid"
    return "invalid"
