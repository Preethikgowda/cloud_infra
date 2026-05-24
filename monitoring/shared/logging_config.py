"""
IntelliWealth – Structured JSON Logging Configuration
Provides production-grade JSON logging with request tracing support.

Features:
  - JSON-formatted log output
  - Request ID propagation (X-Request-ID)
  - Correlation ID tracing
  - Service-level context injection
  - CloudWatch-compatible format
"""

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variables for request tracing
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="-")


# ============================================================
# JSON Formatter
# ============================================================

class JSONFormatter(logging.Formatter):
    """
    Produces JSON log lines compatible with:
    - CloudWatch Logs Insights
    - Elasticsearch / OpenSearch
    - Grafana Loki
    - Datadog
    """

    def __init__(self, service_name: str = "unknown", environment: str = "production"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.000Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
            "request_id": request_id_var.get("-"),
            "correlation_id": correlation_id_var.get("-"),
        }

        # Add source location for errors
        if record.levelno >= logging.WARNING:
            log_entry["source"] = {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        return json.dumps(log_entry, default=str)


# ============================================================
# Request Logging Middleware
# ============================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Assigns a unique request_id to each request
    2. Propagates correlation_id from X-Correlation-ID header
    3. Logs structured request/response data
    4. Adds tracing headers to responses
    """

    def __init__(self, app: FastAPI, service_name: str = "unknown"):
        super().__init__(app)
        self.service_name = service_name
        self.logger = logging.getLogger(f"intelliwealth.{service_name}.http")

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or propagate IDs
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        corr_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # Set context variables for downstream logging
        request_id_var.set(req_id)
        correlation_id_var.set(corr_id)

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            self.logger.error(
                "Request failed: %s %s",
                request.method,
                request.url.path,
                exc_info=True,
            )
            raise
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Structured request log
            self.logger.info(
                "%s %s %d %.1fms",
                request.method,
                request.url.path,
                status_code,
                duration_ms,
                extra={
                    "extra_data": {
                        "http": {
                            "method": request.method,
                            "path": request.url.path,
                            "status_code": status_code,
                            "duration_ms": round(duration_ms, 2),
                            "client_ip": request.client.host if request.client else "-",
                            "user_agent": request.headers.get("user-agent", "-"),
                        },
                        "trace": {
                            "request_id": req_id,
                            "correlation_id": corr_id,
                        },
                    }
                },
            )

            # Add tracing headers to response
            if isinstance(response, Response):
                response.headers["X-Request-ID"] = req_id
                response.headers["X-Correlation-ID"] = corr_id
                response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"


# ============================================================
# Setup Function
# ============================================================

def setup_logging(
    app: FastAPI,
    service_name: str,
    environment: str = "production",
    log_level: str = "INFO",
) -> None:
    """
    Complete structured logging setup for a FastAPI service.

    Usage:
        from monitoring.shared.logging_config import setup_logging
        setup_logging(app, "portfolio-service", "production", "INFO")
    """
    # Configure root logger with JSON formatter
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add JSON handler
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(JSONFormatter(service_name, environment))
    root_logger.addHandler(json_handler)

    # Suppress noisy third-party loggers
    for noisy in ("uvicorn.access", "uvicorn.error", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware, service_name=service_name)

    logging.getLogger(f"intelliwealth.{service_name}").info(
        "Structured logging initialized",
        extra={"extra_data": {"service": service_name, "environment": environment}},
    )
