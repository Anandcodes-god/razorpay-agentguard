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
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.config import settings

PUBLIC_PATHS = {
    "/api/dashboard/stats",
    "/api/dashboard/agents",
    "/api/seed",
}

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/") and request.url.path not in PUBLIC_PATHS and request.url.path != "/api/assess":
            if request.method != "OPTIONS":
                admin_key = settings.admin_api_key
                if not admin_key:
                    return JSONResponse(
                        status_code=503,
                        content={"detail": "Admin API key is not configured"},
                    )
                key = request.headers.get("X-API-Key")
                if key != admin_key:
                    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        return await call_next(request)

app.add_middleware(APIKeyMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Allow all origins for dev
    allow_credentials=False,
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

@app.get("/health")
async def health():
    return {"status": "ok"}
