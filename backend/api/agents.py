from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.database import get_db
from backend.models import Agent
from backend.schemas import AgentCreate, AgentResponse, AgentCreateResponse

router = APIRouter(tags=["Agents"])

@router.get("", response_model=List[AgentResponse], summary="List all agents")
async def list_agents(db: AsyncSession = Depends(get_db)):
    """List all agents with their trust scores."""
    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    return agents

@router.post("", response_model=AgentCreateResponse, summary="Create a new agent")
async def create_agent(agent_data: AgentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new agent."""
    import json, uuid
    data = agent_data.model_dump()
    # Convert scope dict to JSON string for DB storage
    if data.get("scope") and isinstance(data["scope"], dict):
        data["scope"] = json.dumps(data["scope"])
    data["id"] = str(uuid.uuid4())
    new_agent = Agent(**data)
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    return new_agent

@router.get("/{agent_id}", response_model=AgentResponse, summary="Get agent by ID")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific agent by ID with its trust score."""
    result = await db.execute(select(Agent).filter(Agent.id == agent_id))
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
