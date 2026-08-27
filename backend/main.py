from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at startup
    await create_tables()
    yield
    # Run at shutdown

app = FastAPI(
    title="Razorpay AgentGuard",
    description="AI Risk Manager for AI Agents Making Payments",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
try:
    from backend.api.agents import router as agents_router
    from backend.api.contracts import router as contracts_router
    from backend.api.assess import router as assess_router
    from backend.api.simulate import router as simulate_router
    from backend.api.dashboard import router as dashboard_router
    from backend.api.seed_route import router as seed_router

    app.include_router(agents_router, prefix="/api/agents", tags=["Agents"])
    app.include_router(contracts_router, prefix="/api/contracts", tags=["Contracts"])
    app.include_router(assess_router, prefix="/api", tags=["Risk Assessment"])
    app.include_router(simulate_router, prefix="/api/simulate", tags=["Simulation"])
    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(seed_router, prefix="/api", tags=["Setup"])
except ImportError as e:
    print(f"Warning: Could not import some routers: {e}")

@app.get("/")
async def root():
    return {"status": "AgentGuard is running", "version": "1.0.0"}
