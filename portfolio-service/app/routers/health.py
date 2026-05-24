"""
IntelliWealth – Health Check Endpoints
Provides /health, /readiness, and /liveness probes.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", summary="Service health check")
async def health_check():
    """Basic health check – confirms the service is running."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness", summary="Readiness probe")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe – verifies the service can accept traffic.
    Checks database connectivity.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    is_ready = db_status == "connected"

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": {
            "database": db_status,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/liveness", summary="Liveness probe")
async def liveness_check():
    """
    Liveness probe – confirms the process is alive.
    Kubernetes uses this to decide whether to restart the pod.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
