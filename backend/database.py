from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.config import settings

# Ensure we use aiosqlite for async sqlite
db_url = settings.database_url
if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite+aiosqlite:///"):
    db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(db_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with async_session_maker() as session:
        yield session

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if db_url.startswith("sqlite+"):
            columns = await conn.execute(text("PRAGMA table_info(transactions)"))
            if "idempotency_key" not in {row[1] for row in columns.fetchall()}:
                await conn.execute(text("ALTER TABLE transactions ADD COLUMN idempotency_key VARCHAR(128)"))
            await conn.execute(text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_transaction_agent_idempotency "
                "ON transactions (agent_id, idempotency_key)"
            ))
