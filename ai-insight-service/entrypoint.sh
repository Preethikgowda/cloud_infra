#!/bin/bash
set -e

echo "============================================"
echo "  IntelliWealth – AI Insight Service"
echo "  Starting up..."
echo "============================================"

echo "[entrypoint] Provider: ${LLM_PROVIDER:-mock}"
echo "[entrypoint] Environment: ${ENVIRONMENT:-development}"

exec uvicorn app.main:app \
    --host "${AI_SERVICE_HOST:-0.0.0.0}" \
    --port "${AI_SERVICE_PORT:-8002}" \
    --log-level "${AI_SERVICE_LOG_LEVEL:-info}" \
    --access-log
