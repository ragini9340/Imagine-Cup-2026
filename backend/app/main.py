"""
Main FastAPI Application.
Neuro-Privacy Guard Backend - Neural Firewall for BCI Security.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.config import settings
from app.models.schemas import HealthCheck, APIResponse
from app.api.routes import signal, privacy, permissions, threats

# Create FastAPI app
app = FastAPI(
    title="Neuro-Privacy Guard API",
    description="Neural Firewall for Brain-Computer Interface Security",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(
    signal.router,
    prefix="/api/v1/signal",
    tags=["Signal Processing"]
)

app.include_router(
    privacy.router,
    prefix="/api/v1/privacy",
    tags=["Privacy Control"]
)

app.include_router(
    permissions.router,
    prefix="/api/v1/permissions",
    tags=["Permission Management"]
)

app.include_router(
    threats.router,
    prefix="/api/v1/threats",
    tags=["Threat Detection"]
)


# Root endpoints
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint - API information."""
    return APIResponse(
        success=True,
        message="Neuro-Privacy Guard API",
        data={
            "version": settings.APP_VERSION,
            "description": "Neural Firewall for BCI Security",
            "docs": "/docs",
            "health": "/health"
        }
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now()
    )


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    # Seed initial demo data
    from app.core.ai_firewall import permission_gate
    permission_gate.grant_permission("vr-arena", "VR Training Arena", "motor_intent")
    permission_gate.grant_permission("meditation-app", "Mindful Meditation", "emotional_state")
    permission_gate.grant_permission("mind-focus", "Productivity Tracker", "focus_level")

    print("=" * 60)
    print("🧠 Neuro-Privacy Guard Backend Starting...")
    print(f"📡 Version: {settings.APP_VERSION}")
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 CORS Origins: {settings.cors_origins}")
    print(f"🔒 Privacy Level: {settings.DEFAULT_PRIVACY_LEVEL}")
    print("=" * 60)
    print("✅ Neural Firewall Active")
    print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("🛑 Neuro-Privacy Guard shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
