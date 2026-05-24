# IntelliWealth – Observability Stack

Production-grade monitoring, logging, and tracing for the IntelliWealth platform.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION SERVICES                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  Portfolio    │  │  Market      │  │  AI Insight           │   │
│  │  :8000       │  │  :8001       │  │  :8002                │   │
│  │  /metrics    │  │  /metrics    │  │  /metrics             │   │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬────────────┘   │
│         │                  │                      │               │
│         └──────────────────┼──────────────────────┘               │
│                            │ Prometheus scrape                    │
│                    ┌───────▼───────┐                              │
│                    │  Prometheus   │                              │
│                    │  :9090        │                              │
│                    └───────┬───────┘                              │
│                            │ PromQL queries                      │
│                    ┌───────▼───────┐                              │
│                    │   Grafana     │                              │
│                    │   :3001       │                              │
│                    └───────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
                             │
                      CloudWatch Logs
                      (JSON structured)
```

## Quick Start

```bash
docker-compose up --build -d

# Access monitoring
open http://localhost:9090    # Prometheus
open http://localhost:3001    # Grafana (admin / intelliwealth2026)
```

---

## Metrics Collected

### HTTP Metrics (All Services)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_code, service | Total requests |
| `http_request_duration_seconds` | Histogram | method, endpoint, service | Request latency |
| `http_requests_in_progress` | Gauge | method, service | Active requests |
| `http_request_size_bytes` | Histogram | method, endpoint, service | Request payload size |
| `http_response_size_bytes` | Histogram | method, endpoint, service | Response payload size |
| `service_errors_total` | Counter | service, error_type | Unhandled errors |

### AI Service Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `ai_requests_total` | Counter | endpoint, provider, model | AI inference requests |
| `ai_response_duration_seconds` | Histogram | endpoint, provider | AI generation time |
| `ai_tokens_total` | Counter | provider, model | Tokens consumed |
| `ai_errors_total` | Counter | endpoint, error_type | AI inference errors |

### Portfolio Service Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `portfolio_operations_total` | Counter | operation | CRUD operations |
| `portfolio_value_processed_dollars` | Histogram | — | Portfolio values |
| `auth_attempts_total` | Counter | result | Auth success/failure |

### Market Service Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `market_queries_total` | Counter | query_type | Market data queries |
| `risk_assessments_total` | Counter | risk_level | Risk computations |
| `cache_operations_total` | Counter | operation, result | Cache hit/miss |

---

## Grafana Dashboards

### Platform Overview
- Service health status (UP/DOWN)
- Request rate per service
- Error rate percentage
- Latency percentiles (p50/p95/p99)
- In-progress requests
- Status code distribution
- Top endpoints by volume

### Service Intelligence
- AI request rate by endpoint
- AI response time percentiles
- Token usage rate
- AI error rate
- Portfolio operations breakdown
- Risk assessment distribution (pie chart)
- Cache hit rate gauge
- Market query types

---

## Structured Logging

All services emit **JSON-formatted logs** compatible with CloudWatch Logs Insights, Elasticsearch, and Grafana Loki.

### Log Format

```json
{
  "timestamp": "2026-05-24T06:30:00.000Z",
  "level": "INFO",
  "logger": "intelliwealth.portfolio.http",
  "message": "GET /api/v1/portfolio/123 200 45.2ms",
  "service": "portfolio-service",
  "environment": "production",
  "request_id": "a1b2c3d4",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "http": {
      "method": "GET",
      "path": "/api/v1/portfolio/123",
      "status_code": 200,
      "duration_ms": 45.2,
      "client_ip": "10.0.1.15",
      "user_agent": "Mozilla/5.0"
    },
    "trace": {
      "request_id": "a1b2c3d4",
      "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

### Request Tracing

Every request receives:
- **X-Request-ID**: Unique per request (auto-generated or propagated)
- **X-Correlation-ID**: Propagated across services for distributed tracing
- **X-Process-Time-Ms**: Response time in milliseconds

---

## Alert Rules

| Alert | Condition | Severity | Duration |
|-------|-----------|----------|----------|
| ServiceDown | `up == 0` | CRITICAL | 1 min |
| HighErrorRate | `5xx rate > 5%` | WARNING | 5 min |
| HighLatency | `p95 > 2s` | WARNING | 5 min |
| AISlowResponse | `AI p95 > 10s` | WARNING | 3 min |
| AIHighErrorRate | `AI errors > 10%` | CRITICAL | 5 min |
| HighMemoryUsage | `mem > 85%` | WARNING | 5 min |
| PodRestartLoop | `> 3 restarts/hour` | CRITICAL | 5 min |

---

## Integration Guide

### Adding Metrics to a Service

```python
# In service's main.py
from monitoring.shared.metrics import setup_metrics
from monitoring.shared.logging_config import setup_logging

app = FastAPI(...)

# Setup observability
setup_metrics(app, "portfolio-service", "1.0.0", "production")
setup_logging(app, "portfolio-service", "production", "INFO")
```

### Adding Custom Metrics

```python
from monitoring.shared.metrics import create_portfolio_metrics

metrics = create_portfolio_metrics()
metrics["portfolio_operations_total"].labels(operation="create").inc()
```

### CloudWatch Integration

JSON logs are automatically compatible with CloudWatch Logs Insights:

```sql
-- CloudWatch query: Find slow requests
fields @timestamp, data.http.path, data.http.duration_ms
| filter data.http.duration_ms > 1000
| sort @timestamp desc
| limit 20
```

---

## File Structure

```
monitoring/
├── shared/
│   ├── __init__.py
│   ├── metrics.py              # Prometheus middleware + factories
│   └── logging_config.py       # JSON logging + request tracing
├── prometheus/
│   ├── prometheus.yml           # Scrape config
│   └── alerts.yml               # Alert rules
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── datasources.yml  # Prometheus datasource
    │   └── dashboards/
    │       └── dashboards.yml   # Auto-load config
    └── dashboards/
        ├── platform-overview.json
        └── service-intelligence.json
```
