"""
IntelliWealth – AI Insight Service Application Entry Point
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import health, ai

settings = get_settings()

# ---- Logging ----
logging.basicConfig(
    level=getattr(logging, settings.AI_SERVICE_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("intelliwealth.ai")


# ---- Lifespan ----
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  IntelliWealth AI Insight Service – Starting")
    logger.info("  Environment: %s", settings.ENVIRONMENT)
    logger.info("  Version: %s", settings.APP_VERSION)
    logger.info("  LLM Provider: %s", settings.LLM_PROVIDER)
    logger.info("  Model: %s", settings.BEDROCK_MODEL_ID if settings.LLM_PROVIDER == "bedrock" else "mock-analyst-v1")
    logger.info("=" * 60)
    yield
    logger.info("IntelliWealth AI Insight Service – Shutting down.")


# ---- Application ----
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-powered portfolio intelligence service for the IntelliWealth platform. "
        "Generates analytical narratives explaining portfolio composition, risk factors, "
        "market impact, and scenario projections. "
        "**This service does NOT provide investment advice.** "
        "It only explains and narrates portfolio state."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request Logging Middleware ----
@app.middleware("http")
async def request_logging_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
    return response


# ---- Global Exception Handler ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred in the AI service.",
            "error_type": type(exc).__name__,
            "path": str(request.url.path),
        },
    )


# ---- Routers ----
app.include_router(health.router)
app.include_router(ai.router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "provider": settings.LLM_PROVIDER,
        "docs": "/docs",
        "health": "/health",
        "compliance": "This service does NOT provide investment advice.",
        "endpoints": [
            "POST /api/v1/ai/analyze",
            "POST /api/v1/ai/risk-summary",
            "POST /api/v1/ai/scenario-analysis",
            "POST /api/v1/ai/explain-portfolio",
        ],
    }
