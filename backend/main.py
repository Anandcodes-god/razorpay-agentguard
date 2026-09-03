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
import os
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

ADMIN_KEY = os.environ.get("ADMIN_API_KEY", "dev-secret")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            if request.method != "OPTIONS":
                key = request.headers.get("X-API-Key")
                if key != ADMIN_KEY:
                    raise HTTPException(status_code=401, detail="Unauthorized")
        return await call_next(request)

app.add_middleware(APIKeyMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register routers
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

@app.get("/")
async def root():
    return {"status": "AgentGuard is running", "version": "1.0.0"}
