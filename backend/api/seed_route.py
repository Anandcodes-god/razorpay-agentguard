from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.seed.seed_data import seed_all
from backend.config import settings

router = APIRouter(tags=["Setup"])

@router.post("/seed", summary="Seed the database with demo data")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with initial agents, contracts, and demo data."""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Demo seeding is disabled")
    await seed_all(db)
    return {"message": "Database seeded successfully"}
