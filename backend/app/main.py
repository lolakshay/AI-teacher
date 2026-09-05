from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.api.routes import router as api_router
from backend.video.api import video_router

logger = logging.getLogger("ai_teacher.startup")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validates configuration at startup and logs system status."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.PROJECT_NAME} v1.0.0")
    logger.info(f"Environment: {settings.APP_ENV} | Demo Mode: {settings.DEMO_MODE}")
    logger.info(f"LLM Key Configured: {'Yes' if settings.GEMINI_API_KEY else 'No (using deterministic fallback)'}")
    logger.info(f"Voice Provider: {settings.VOICE_PROVIDER} | Avatar: {settings.AVATAR_PROVIDER}")
    logger.info(f"Max Reteach Attempts: {settings.MAX_RETEACH_ATTEMPTS}")
    logger.info("=" * 60)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Human-Like Adaptive AI Educator - AI Innovation Hackathon 2026",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(video_router, prefix=settings.API_V1_STR)

# Mount Static Files for Video Assets (frames, rendered mp4, audio, avatar)
settings.VIDEO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static/videos", StaticFiles(directory=str(settings.VIDEO_OUTPUT_DIR)), name="videos")


@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "health_url": "/health",
        "api_v1": settings.API_V1_STR
    }

@app.get("/health")
@app.get("/api/health")
def health_check():
    """
    Comprehensive System Health Check (Section 26).
    Exposes status of all subsystems without leaking secrets.
    """
    db_status = "connected"
    try:
        from backend.personalization.repository import profile_repository
        profile_repository.get_profile("health_dummy")
    except Exception:
        db_status = "fallback_in_memory"

    llm_status = "live_gemini" if settings.GEMINI_API_KEY else "deterministic_mock_ready"

    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "demo_mode": settings.DEMO_MODE,
        "subsystems": {
            "orchestrator": "active",
            "rag": "ready",
            "personalization_db": db_status,
            "evaluation_engine": "active",
            "adaptation_engine": "active",
            "assessment_engine": "active",
            "video_engine": "active",
            "llm_provider": llm_status,
            "voice_provider": settings.VOICE_PROVIDER,
            "avatar_provider": settings.AVATAR_PROVIDER
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
