from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.seed.seed_data import seed_all

router = APIRouter(tags=["Setup"])

@router.post("/seed", summary="Seed the database with demo data")
async def seed_database(db: AsyncSession = Depends(get_db)):
    """Seed the database with initial agents, contracts, and demo data."""
    await seed_all(db)
    return {"message": "Database seeded successfully"}
