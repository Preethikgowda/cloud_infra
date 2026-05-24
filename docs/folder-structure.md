# IntelliWealth – Complete Folder Structure

## Root Directory

```
NewIntelliwealth/
│
├── README.md                               # Project overview & quick start
├── docker-compose.yml                      # 8-container local orchestration
├── .env.example                            # Environment variable template
├── .gitignore                              # Git ignore rules
│
├── docs/                                   # Documentation
│   ├── architecture.md                     # System design & risk engine
│   ├── deployment-guide.md                 # Docker & EKS deployment
│   ├── api-documentation.md                # Complete API reference
│   ├── service-communication.md            # Service interaction diagrams
│   ├── folder-structure.md                 # This file
│   └── roadmap.md                          # Future AI/agent plans
│
├── frontend/                               # React SPA
├── portfolio-service/                      # Portfolio management API
├── market-service/                         # Market data & risk engine
├── ai-insight-service/                     # AI-powered insights
├── monitoring/                             # Observability stack
├── k8s/                                    # Kubernetes manifests
└── docker/                                 # Docker utilities
```

---

## Frontend (`frontend/`)

```
frontend/
├── Dockerfile                              # Multi-stage: node:20 → nginx:1.27
├── nginx.conf                              # SPA routing config
├── package.json
├── package-lock.json
├── tsconfig.json
├── vite.config.ts
├── index.html
│
├── public/                                 # Static assets
│
└── src/
    ├── App.tsx                             # Root component + routing
    ├── main.tsx                            # Entry point
    ├── index.css                           # Global styles + design tokens
    │
    ├── components/
    │   ├── Layout.tsx                      # App shell with sidebar
    │   ├── Navbar.tsx                      # Top navigation bar
    │   ├── Sidebar.tsx                     # Side navigation panel
    │   └── ProtectedRoute.tsx             # Auth guard component
    │
    ├── pages/
    │   ├── Login.tsx                       # Authentication page
    │   ├── Dashboard.tsx                   # Main dashboard
    │   ├── PortfolioOverview.tsx           # Portfolio listing
    │   ├── PortfolioHistory.tsx            # Historical performance
    │   ├── AssetAllocation.tsx             # Allocation visualization
    │   ├── Profile.tsx                     # User profile
    │   └── Admin.tsx                       # Admin panel
    │
    ├── services/
    │   └── api.ts                          # Axios HTTP client
    │
    └── types/
        └── index.ts                        # TypeScript interfaces
```

---

## Portfolio Service (`portfolio-service/`)

```
portfolio-service/
├── Dockerfile                              # python:3.12-slim, port 8000
├── .dockerignore
├── entrypoint.sh                           # Alembic migrate + uvicorn
├── requirements.txt                        # FastAPI, SQLAlchemy, JWT
│
├── alembic.ini                             # Migration config
├── alembic/
│   ├── env.py                              # Migration environment
│   ├── script.py.mako                      # Template
│   └── versions/
│       └── 001_initial_schema.py           # customers, portfolios, assets, etc.
│
└── app/
    ├── __init__.py
    ├── config.py                           # pydantic-settings
    ├── database.py                         # SQLAlchemy engine + session
    ├── main.py                             # FastAPI app, CORS, middleware
    │
    ├── auth/
    │   ├── __init__.py
    │   ├── jwt_handler.py                  # Token create/verify
    │   └── dependencies.py                 # get_current_user Depends()
    │
    ├── models/
    │   ├── __init__.py
    │   ├── customer.py                     # Customer ORM model
    │   ├── portfolio.py                    # Portfolio ORM model
    │   ├── asset.py                        # Asset ORM model
    │   ├── transaction.py                  # Transaction ORM model
    │   └── portfolio_history.py            # History ORM model
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── customer.py                     # Customer Pydantic schemas
    │   ├── portfolio.py                    # Portfolio schemas
    │   ├── asset.py                        # Asset schemas
    │   ├── transaction.py                  # Transaction schemas
    │   └── portfolio_history.py            # History schemas
    │
    ├── routers/
    │   ├── __init__.py
    │   ├── health.py                       # /health, /readiness, /liveness
    │   ├── auth.py                         # /auth/login, /auth/refresh
    │   ├── customers.py                    # /customers CRUD
    │   └── portfolios.py                   # /portfolio CRUD + allocation
    │
    └── services/
        ├── __init__.py
        ├── customer_service.py             # Customer business logic
        └── portfolio_service.py            # Portfolio business logic
```

---

## Market Service (`market-service/`)

```
market-service/
├── Dockerfile                              # python:3.12-slim, port 8001
├── .dockerignore
├── entrypoint.sh                           # Alembic + seed + uvicorn
├── requirements.txt                        # FastAPI, SQLAlchemy, Redis
├── README.md
│
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_market_schema.py            # market_data, sector_data, risk_metrics
│
└── app/
    ├── __init__.py
    ├── config.py                           # Settings + risk thresholds
    ├── database.py                         # SQLAlchemy engine
    ├── redis_client.py                     # Redis pool + CacheService
    ├── main.py                             # FastAPI app
    ├── seed.py                             # 1,729 market data records
    │
    ├── models/
    │   ├── __init__.py
    │   ├── market_data.py                  # Price, volume, market cap
    │   ├── sector_data.py                  # Sector performance
    │   ├── risk_metrics.py                 # Risk scores (JSONB)
    │   └── portfolio_assets.py             # Cross-service data reader
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── market_data.py                  # Asset/trend/volatility responses
    │   ├── sector_data.py                  # Sector analysis response
    │   └── risk_metrics.py                 # Risk assessment + concentration
    │
    ├── routers/
    │   ├── __init__.py
    │   ├── health.py                       # Health + readiness (DB+Redis)
    │   └── market.py                       # 5 market endpoints
    │
    └── services/
        ├── __init__.py
        ├── market_service.py               # Asset query, trends, volatility
        └── risk_engine.py                  # HHI, diversification, risk scoring
```

---

## AI Insight Service (`ai-insight-service/`)

```
ai-insight-service/
├── Dockerfile                              # python:3.12-slim, port 8002
├── .dockerignore
├── entrypoint.sh                           # Uvicorn launch
├── requirements.txt                        # FastAPI, LangChain, Boto3
├── README.md
│
└── app/
    ├── __init__.py
    ├── config.py                           # LLM provider + AWS config
    ├── dependencies.py                     # DI factory: mock ↔ bedrock
    ├── main.py                             # FastAPI app
    │
    ├── providers/
    │   ├── __init__.py
    │   ├── base.py                         # LLMProvider ABC interface
    │   ├── mock_provider.py                # Template-based (active)
    │   └── bedrock_provider.py             # AWS Bedrock Claude (prepared)
    │
    ├── schemas/
    │   ├── __init__.py
    │   ├── analyze.py                      # Analysis request/response
    │   ├── risk_summary.py                 # Risk narration schemas
    │   ├── scenario.py                     # Scenario analysis schemas
    │   └── explain.py                      # Plain-language schemas
    │
    ├── routers/
    │   ├── __init__.py
    │   ├── health.py                       # Health + metrics + readiness
    │   └── ai.py                           # 4 AI endpoints with DI
    │
    └── services/
        ├── __init__.py
        └── ai_service.py                   # Orchestrator: schema → prompt → provider
```

---

## Monitoring (`monitoring/`)

```
monitoring/
├── README.md                               # Observability documentation
│
├── shared/
│   ├── __init__.py
│   ├── metrics.py                          # Prometheus middleware + factories
│   └── logging_config.py                   # JSON logging + request tracing
│
├── prometheus/
│   ├── prometheus.yml                      # Scrape config (3 services)
│   └── alerts.yml                          # 7 alert rules
│
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── datasources.yml             # Prometheus datasource
    │   └── dashboards/
    │       └── dashboards.yml              # Auto-load config
    └── dashboards/
        ├── platform-overview.json          # 8 panels
        └── service-intelligence.json       # 11 panels
```

---

## Kubernetes (`k8s/`)

```
k8s/
├── base/
│   ├── namespace.yaml                      # intelliwealth namespace
│   ├── ingress.yaml                        # ALB ingress + path routing
│   │
│   ├── postgres/
│   │   ├── secret.yaml                     # DB credentials
│   │   ├── configmap.yaml                  # Tuning params
│   │   ├── pvc.yaml                        # 20Gi gp3 storage
│   │   ├── deployment.yaml                 # Single replica
│   │   └── service.yaml                    # ClusterIP :5432
│   │
│   ├── redis/
│   │   ├── configmap.yaml                  # redis.conf
│   │   ├── deployment.yaml                 # Single replica
│   │   └── service.yaml                    # ClusterIP :6379
│   │
│   ├── portfolio-service/
│   │   ├── secret.yaml                     # DATABASE_URL, JWT
│   │   ├── configmap.yaml                  # CORS, log level
│   │   ├── deployment.yaml                 # 2 replicas, 3 probes
│   │   ├── service.yaml                    # ClusterIP :8000
│   │   └── hpa.yaml                        # 2→8 pods
│   │
│   ├── market-service/
│   │   ├── secret.yaml                     # DATABASE_URL, REDIS_URL
│   │   ├── configmap.yaml                  # Cache TTLs
│   │   ├── deployment.yaml                 # 2 replicas, 3 probes
│   │   ├── service.yaml                    # ClusterIP :8001
│   │   └── hpa.yaml                        # 2→6 pods
│   │
│   ├── ai-insight-service/
│   │   ├── secret.yaml                     # AWS credentials
│   │   ├── configmap.yaml                  # LLM config
│   │   ├── deployment.yaml                 # 2 replicas, 3 probes
│   │   ├── service.yaml                    # ClusterIP :8002
│   │   └── hpa.yaml                        # 2→10 pods
│   │
│   ├── frontend/
│   │   ├── configmap.yaml                  # Nginx config
│   │   ├── deployment.yaml                 # 2 replicas
│   │   ├── service.yaml                    # ClusterIP :80
│   │   └── hpa.yaml                        # 2→6 pods
│   │
│   └── monitoring/
│       ├── prometheus.yaml                 # ConfigMap + Deploy + RBAC
│       └── grafana.yaml                    # ConfigMap + Secret + Deploy
│
└── (legacy single-file manifests - superseded by base/)
```

---

## File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `frontend/` | ~25 | React SPA |
| `portfolio-service/` | ~25 | Portfolio API |
| `market-service/` | ~30 | Market & risk |
| `ai-insight-service/` | ~23 | AI insights |
| `monitoring/` | 12 | Observability |
| `k8s/base/` | 31 | Kubernetes |
| `docs/` | 6 | Documentation |
| **Total** | **~155+** | |
