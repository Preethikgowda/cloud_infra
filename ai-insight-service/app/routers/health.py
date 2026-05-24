"""
IntelliWealth – AI Service Health & Metrics Endpoints
"""

from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends

from app.config import get_settings
from app.dependencies import get_llm_provider
from app.providers.base import LLMProvider
from app.services.ai_service import AIInsightService

router = APIRouter(tags=["Health"])
settings = get_settings()

# Singleton service instance for metrics
_ai_service = AIInsightService()


def get_ai_service() -> AIInsightService:
    return _ai_service


@router.get("/health", summary="Service health check")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "provider": settings.LLM_PROVIDER,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness", summary="Readiness probe")
async def readiness_check(provider: LLMProvider = Depends(get_llm_provider)):
    """Readiness probe – verifies LLM provider is available."""
    provider_health = await provider.health_check()
    is_ready = provider_health.get("status") == "healthy"

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "llm_provider": provider_health,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/liveness", summary="Liveness probe")
async def liveness_check():
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/metrics", summary="Service metrics", tags=["Monitoring"])
async def get_metrics():
    """Return AI service operational metrics."""
    metrics = _ai_service.get_metrics()
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.LLM_PROVIDER,
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat(),
    }
