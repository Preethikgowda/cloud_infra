# IntelliWealth – Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                React + TypeScript + Tailwind                 │
│                      (Nginx / Port 3000)                     │
└────────────────────────────┬─────────────────────────────────┘
                             │ REST API (JSON)
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌────────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ PORTFOLIO SERVICE  │ │ MARKET SVC   │ │ AI INSIGHT SERVICE   │
│ Port 8000          │ │ Port 8001    │ │ Port 8002            │
│                    │ │              │ │                      │
│ Auth / Customers   │ │ Assets/Trends│ │ Analyze / Explain    │
│ Portfolios / CRUD  │ │ Volatility   │ │ Risk Summary         │
│ JWT Handler        │ │ Risk Engine  │ │ Scenario Analysis    │
│ SQLAlchemy ORM     │ │ Cache Service│ │ LLM Provider (DI)    │
└─────────┬──────────┘ └──────┬───────┘ └──────────┬───────────┘
          │                   │                     │
          │                   │          ┌──────────▼──────────┐
          │                   │          │ MockProvider (dev)  │
          │                   │          │ BedrockProvider     │
          │                   │          │ (production-ready)  │
          │                   │          └─────────────────────┘
    ┌─────▼───────────────────▼────┐
    │       POSTGRESQL 16         │
    │                              │
    │  customers │ portfolios      │
    │  assets │ transactions       │
    │  portfolio_history           │
    │  market_data │ sector_data   │
    │  risk_metrics                │
    └──────────────────────────────┘
                  │
            ┌─────▼─────┐
            │  REDIS 7  │
            │  Cache    │
            └───────────┘
```

## Database Schema (ERD)

```
Portfolio Service Tables:
  customers 1───* portfolios 1───* assets 1───* transactions
                      │
                      1───* portfolio_history

Market Service Tables:
  market_data (standalone)
  sector_data (standalone)
  risk_metrics ──FK──> portfolios.id
```

### Table Details

| Table              | Primary Key | Service          | Key Foreign Keys           |
|--------------------|-------------|------------------|----------------------------|
| customers          | id (UUID)   | Portfolio Service| –                          |
| portfolios         | id (UUID)   | Portfolio Service| customer_id → customers.id |
| assets             | id (UUID)   | Portfolio Service| portfolio_id → portfolios.id |
| transactions       | id (UUID)   | Portfolio Service| asset_id → assets.id       |
| portfolio_history  | id (UUID)   | Portfolio Service| portfolio_id → portfolios.id |
| market_data        | id (UUID)   | Market Service   | –                          |
| sector_data        | id (UUID)   | Market Service   | –                          |
| risk_metrics       | id (UUID)   | Market Service   | portfolio_id (logical FK)  |

## API Endpoints

### Portfolio Service (Port 8000)

| Method | Path                              | Auth     | Description               |
|--------|-----------------------------------|----------|---------------------------|
| POST   | /api/v1/auth/login                | Public   | Authenticate user         |
| POST   | /api/v1/auth/refresh              | Public   | Refresh access token      |
| POST   | /api/v1/customers                 | Public   | Create customer           |
| GET    | /api/v1/customers/{id}            | Bearer   | Get customer              |
| PUT    | /api/v1/customers/{id}            | Bearer   | Update customer           |
| GET    | /api/v1/customers                 | Admin    | List all customers        |
| POST   | /api/v1/portfolio                 | Bearer   | Create portfolio          |
| GET    | /api/v1/portfolio/{id}            | Bearer   | Get portfolio             |
| POST   | /api/v1/portfolio/add-asset       | Bearer   | Add asset                 |
| PUT    | /api/v1/portfolio/update-asset/{id}| Bearer  | Update asset              |
| DELETE | /api/v1/portfolio/remove-asset/{id}| Bearer  | Remove asset              |
| GET    | /api/v1/portfolio/allocation/{id} | Bearer   | Get allocation            |
| GET    | /api/v1/portfolio/history/{id}    | Bearer   | Get history               |

### Market Intelligence Service (Port 8001)

| Method | Path                           | Auth   | Description               |
|--------|--------------------------------|--------|---------------------------|
| GET    | /api/v1/market/assets          | Public | Latest market asset data  |
| GET    | /api/v1/market/trends          | Public | Asset price trend analysis|
| GET    | /api/v1/market/volatility      | Public | Market volatility metrics |
| GET    | /api/v1/market/risk            | Public | Portfolio risk assessment |
| GET    | /api/v1/market/sector-analysis | Public | Sector performance report |

### AI Insight Service (Port 8002)

| Method | Path                           | Auth   | Description                |
|--------|--------------------------------|--------|----------------------------|
| POST   | /api/v1/ai/analyze             | Public | Portfolio composition analysis |
| POST   | /api/v1/ai/risk-summary        | Public | Risk narration from metrics    |
| POST   | /api/v1/ai/scenario-analysis   | Public | What-if scenario projection    |
| POST   | /api/v1/ai/explain-portfolio   | Public | Plain-language explanation     |

### Health Probes (All Services)

| Method | Path        | Description     |
|--------|-------------|-----------------|
| GET    | /health     | Health check    |
| GET    | /readiness  | Readiness probe |
| GET    | /liveness   | Liveness probe  |
| GET    | /metrics    | Operational metrics (AI only) |

## Technology Stack

| Layer      | Technology            | Rationale                                      |
|------------|-----------------------|------------------------------------------------|
| Frontend   | React + TypeScript    | Type safety, component reuse, large ecosystem  |
| Styling    | Tailwind CSS v4       | Utility-first, rapid prototyping               |
| Charts     | Recharts              | Declarative, React-native charting             |
| Backend    | FastAPI               | Async-first, auto OpenAPI docs, Pydantic       |
| ORM        | SQLAlchemy 2.0        | Mature, flexible, great migration support      |
| Migrations | Alembic               | Native SQLAlchemy integration                  |
| Auth       | JWT (python-jose)     | Stateless, scalable authentication             |
| AI / LLM   | LangChain + Bedrock   | Provider abstraction, RAG-ready                |
| Database   | PostgreSQL 16         | ACID compliance, UUID support, production-grade|
| Caching    | Redis 7               | Sub-ms reads, TTL-based expiry, LRU eviction   |
| Container  | Docker + Compose      | Reproducible environments                      |
| Orchestration | Kubernetes         | Production scaling and self-healing            |

## Risk Engine Architecture

```
Portfolio Assets ──> Allocation Calculator ──┐
                                             │
    ┌────────────────────────────────────────▼──────────┐
    │               RISK ENGINE                         │
    │                                                    │
    │  ┌──────────────┐  ┌──────────────────┐           │
    │  │Concentration │  │Sector Exposure   │           │
    │  │(HHI Index)   │  │(Type → Sector)   │           │
    │  └──────┬───────┘  └────────┬─────────┘           │
    │         │                    │                      │
    │  ┌──────▼───────┐  ┌───────▼──────────┐           │
    │  │Diversification│  │Weighted         │           │
    │  │Score (0–100) │  │Volatility       │           │
    │  └──────┬───────┘  └────────┬─────────┘           │
    │         │                    │                      │
    │  ┌──────▼────────────────────▼──────────────┐     │
    │  │         Risk Score Calculator             │     │
    │  │  25% concentration + 25% diversification  │     │
    │  │  30% volatility   + 20% equity exposure   │     │
    │  │                                           │     │
    │  │  RULE: equity > 80% → force HIGH          │     │
    │  │  RULE: gold → reduces score by up to 15%  │     │
    │  └──────────────┬───────────────────────────┘     │
    │                 │                                  │
    │  ┌──────────────▼──────────────┐                   │
    │  │ Recommendation Generator    │                   │
    │  └─────────────────────────────┘                   │
    └────────────────────────────────────────────────────┘
```

## Phase Scope

### Phase 1 (Complete)
- ✅ Project structure
- ✅ Frontend skeleton (7 pages)
- ✅ Portfolio Service (full CRUD)
- ✅ PostgreSQL integration
- ✅ JWT Authentication
- ✅ Docker environment

### Phase 2 (Complete)
- ✅ Market Intelligence Service
- ✅ Redis caching layer
- ✅ Risk analytics engine
- ✅ Market data seeding
- ✅ Sector analysis
- ✅ Kubernetes manifests for market-service + Redis

### Phase 3 (Complete)
- ✅ AI Insight Service
- ✅ LLM Provider abstraction (MockProvider + BedrockProvider)
- ✅ Portfolio analysis & explanation endpoints
- ✅ Risk narration & scenario analysis
- ✅ Dependency injection for provider swapping
- ✅ Compliance enforcement (no investment advice)
- ✅ Kubernetes manifest for AI service

### Future Phases (Not Implemented)
- ❌ Real-time WebSocket updates
- ❌ Email notifications
- ❌ CI/CD pipeline
- ❌ External market data API integration
- ❌ LangChain RAG pipeline activation
