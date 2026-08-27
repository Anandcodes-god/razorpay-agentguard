from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone, timedelta
import json
import uuid

from backend.database import get_db
from backend.models import IntentContract
from backend.schemas import IntentContractCreate, IntentContractResponse

router = APIRouter(tags=["Intent Contracts"])


@router.post("", summary="Create intent contract")
async def create_contract(contract_data: IntentContractCreate, db: AsyncSession = Depends(get_db)):
    """
    Create an intent contract from a raw instruction.
    Optionally uses LLM to parse the instruction into structured fields.
    """
    purpose = None
    categories = "[]"
    max_amount = contract_data.max_amount or 500000  # Default ₹5,000
    merchant_constraints = "{}"
    requires_confirmation_above = max_amount

    # Try to use LLM to parse the instruction
    try:
        from backend.services.llm_client import get_llm_client
        llm = get_llm_client()
        parsed = await llm.parse_intent(contract_data.raw_instruction)
        if parsed:
            purpose = parsed.get("purpose", purpose)
            cats = parsed.get("categories", [])
            if cats:
                categories = json.dumps(cats)
            if parsed.get("max_amount"):
                max_amount = parsed["max_amount"]
            mc = parsed.get("merchant_constraints")
            if mc:
                merchant_constraints = json.dumps(mc) if isinstance(mc, (dict, list)) else "{}"
            if parsed.get("requires_confirmation_above"):
                requires_confirmation_above = parsed["requires_confirmation_above"]
    except Exception:
        # LLM unavailable — use defaults
        pass

    # Override with explicitly provided max_amount
    if contract_data.max_amount:
        max_amount = contract_data.max_amount

    expires_at = datetime.now(timezone.utc) + timedelta(hours=contract_data.expires_in_hours)

    contract = IntentContract(
        id=str(uuid.uuid4()),
        agent_id=contract_data.agent_id,
        raw_instruction=contract_data.raw_instruction,
        purpose=purpose,
        categories=categories,
        max_amount=max_amount,
        currency="INR",
        merchant_constraints=merchant_constraints,
        requires_confirmation_above=requires_confirmation_above,
        expires_at=expires_at,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)

    return {
        "id": contract.id,
        "agent_id": contract.agent_id,
        "raw_instruction": contract.raw_instruction,
        "purpose": contract.purpose,
        "categories": json.loads(contract.categories) if contract.categories else [],
        "max_amount": contract.max_amount,
        "merchant_constraints": json.loads(contract.merchant_constraints) if contract.merchant_constraints else {},
        "expires_at": contract.expires_at.isoformat() if contract.expires_at else None,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
    }


@router.get("/{contract_id}", summary="Get intent contract")
async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    """Get an intent contract by ID."""
    result = await db.execute(select(IntentContract).filter(IntentContract.id == contract_id))
    contract = result.scalars().first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return {
        "id": contract.id,
        "agent_id": contract.agent_id,
        "raw_instruction": contract.raw_instruction,
        "purpose": contract.purpose,
        "categories": json.loads(contract.categories) if contract.categories else [],
        "max_amount": contract.max_amount,
        "merchant_constraints": json.loads(contract.merchant_constraints) if contract.merchant_constraints else {},
        "expires_at": contract.expires_at.isoformat() if contract.expires_at else None,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
    }


@router.get("", summary="List all intent contracts")
async def list_contracts(db: AsyncSession = Depends(get_db)):
    """List all intent contracts."""
    result = await db.execute(select(IntentContract))
    contracts = result.scalars().all()
    return [
        {
            "id": c.id,
            "agent_id": c.agent_id,
            "raw_instruction": c.raw_instruction,
            "purpose": c.purpose,
            "categories": json.loads(c.categories) if c.categories else [],
            "max_amount": c.max_amount,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in contracts
    ]
