"""
IntelliWealth – Prometheus Metrics Middleware
Shared middleware providing request-level metrics for all FastAPI services.

Metrics exposed:
  - http_requests_total (counter)
  - http_request_duration_seconds (histogram)
  - http_requests_in_progress (gauge)
  - http_request_size_bytes (histogram)
  - http_response_size_bytes (histogram)

Service-specific metrics:
  - service_info (gauge with version/environment labels)
  - service_errors_total (counter)
"""

import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    REGISTRY,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse


# ============================================================
# Core HTTP Metrics
# ============================================================

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "service"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "service"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently in progress",
    ["method", "service"],
)

HTTP_REQUEST_SIZE = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint", "service"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000),
)

HTTP_RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "service"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000),
)

SERVICE_ERRORS_TOTAL = Counter(
    "service_errors_total",
    "Total service errors",
    ["service", "error_type"],
)

SERVICE_INFO = Info(
    "service",
    "Service information",
)


# ============================================================
# Service-Specific Metric Factories
# ============================================================

def create_ai_metrics():
    """Create AI-specific metrics."""
    return {
        "ai_requests_total": Counter(
            "ai_requests_total",
            "Total AI inference requests",
            ["endpoint", "provider", "model"],
        ),
        "ai_response_duration_seconds": Histogram(
            "ai_response_duration_seconds",
            "AI response generation time in seconds",
            ["endpoint", "provider"],
            buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
        ),
        "ai_tokens_total": Counter(
            "ai_tokens_total",
            "Total tokens used by AI provider",
            ["provider", "model"],
        ),
        "ai_errors_total": Counter(
            "ai_errors_total",
            "Total AI inference errors",
            ["endpoint", "error_type"],
        ),
    }


def create_portfolio_metrics():
    """Create portfolio-specific metrics."""
    return {
        "portfolio_operations_total": Counter(
            "portfolio_operations_total",
            "Total portfolio operations",
            ["operation"],
        ),
        "portfolio_value_processed": Histogram(
            "portfolio_value_processed_dollars",
            "Portfolio values processed",
            buckets=(1000, 10000, 50000, 100000, 500000, 1000000, 5000000),
        ),
        "auth_attempts_total": Counter(
            "auth_attempts_total",
            "Authentication attempts",
            ["result"],
        ),
    }


def create_market_metrics():
    """Create market-specific metrics."""
    return {
        "market_queries_total": Counter(
            "market_queries_total",
            "Total market data queries",
            ["query_type"],
        ),
        "risk_assessments_total": Counter(
            "risk_assessments_total",
            "Total risk assessments computed",
            ["risk_level"],
        ),
        "cache_operations_total": Counter(
            "cache_operations_total",
            "Cache operations",
            ["operation", "result"],
        ),
    }


# ============================================================
# Middleware
# ============================================================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that automatically instruments all HTTP requests
    with Prometheus metrics.
    """

    def __init__(self, app: FastAPI, service_name: str = "unknown"):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = self._normalize_path(request.url.path)

        # Track in-progress requests
        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=method, service=self.service_name
        ).inc()

        # Request size
        content_length = request.headers.get("content-length", 0)
        HTTP_REQUEST_SIZE.labels(
            method=method, endpoint=path, service=self.service_name
        ).observe(int(content_length or 0))

        # Time the request
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            SERVICE_ERRORS_TOTAL.labels(
                service=self.service_name,
                error_type=type(exc).__name__,
            ).inc()
            raise
        finally:
            duration = time.perf_counter() - start_time

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=path,
                status_code=str(status_code),
                service=self.service_name,
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=method, endpoint=path, service=self.service_name
            ).observe(duration)

            HTTP_REQUESTS_IN_PROGRESS.labels(
                method=method, service=self.service_name
            ).dec()

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize URL paths to prevent cardinality explosion.
        Replaces UUIDs and numeric IDs with placeholders.
        """
        import re
        # Replace UUIDs
        path = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "{id}",
            path,
        )
        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)
        return path


# ============================================================
# Metrics Endpoint
# ============================================================

def add_metrics_endpoint(app: FastAPI) -> None:
    """Add /metrics endpoint that exposes Prometheus metrics."""

    @app.get("/metrics", tags=["Monitoring"], include_in_schema=False)
    async def metrics():
        return StarletteResponse(
            content=generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST,
        )


def setup_metrics(
    app: FastAPI,
    service_name: str,
    service_version: str = "1.0.0",
    environment: str = "production",
) -> None:
    """
    Complete metrics setup for a FastAPI service.

    Usage:
        from monitoring.shared.metrics import setup_metrics
        setup_metrics(app, "portfolio-service", "1.0.0", "production")
    """
    # Set service info
    SERVICE_INFO.info({
        "service_name": service_name,
        "version": service_version,
        "environment": environment,
    })

    # Add middleware
    app.add_middleware(PrometheusMiddleware, service_name=service_name)

    # Add /metrics endpoint
    add_metrics_endpoint(app)
