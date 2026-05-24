# IntelliWealth – Market Intelligence Service

Enterprise-grade market analytics and risk intelligence engine for the IntelliWealth platform.

> **This is NOT a trading service.** It provides market data storage, asset tracking, risk analytics, and portfolio intelligence.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MARKET INTELLIGENCE SERVICE                  │
│              FastAPI / Port 8001                          │
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │  Market     │  │  Risk      │  │  Health    │        │
│  │  Router     │  │  Engine    │  │  Router    │        │
│  └─────┬──────┘  └─────┬──────┘  └────────────┘        │
│        │               │                                 │
│  ┌─────▼──────┐  ┌─────▼──────┐                         │
│  │  Market    │  │  Risk      │                         │
│  │  Service   │  │  Engine    │                         │
│  └─────┬──────┘  └─────┬──────┘                         │
│        │               │                                 │
│   ┌────▼───────────────▼────┐                            │
│   │     Cache Service       │◄──── Redis                 │
│   └────────────┬────────────┘                            │
│                │                                         │
│         ┌──────▼──────┐                                  │
│         │  SQLAlchemy  │                                  │
│         └──────┬──────┘                                  │
└────────────────┼────────────────────────────────────────┘
                 │
                 ▼
          ┌──────────────┐
          │ PostgreSQL 16 │
          └──────────────┘
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/market/assets` | Latest market data for tracked assets |
| GET | `/api/v1/market/trends` | Price trend analysis for a specific asset |
| GET | `/api/v1/market/volatility` | Market-wide volatility metrics by asset type |
| GET | `/api/v1/market/risk` | Portfolio risk assessment with intelligence |
| GET | `/api/v1/market/sector-analysis` | Sector performance and sentiment analysis |
| GET | `/health` | Service health check |
| GET | `/readiness` | Readiness probe (DB + Redis) |
| GET | `/liveness` | Liveness probe |

## Risk Engine

The risk engine computes five core metrics:

| Metric | Description |
|--------|-------------|
| **Concentration** | HHI-based score measuring portfolio concentration (0–100) |
| **Sector Exposure** | Allocation mapped to sectors (Equity, Fixed Income, etc.) |
| **Diversification** | Score based on asset type count, distribution evenness, and gold bonus |
| **Volatility** | Portfolio-weighted annualized volatility estimate |
| **Risk Level** | Classification: LOW / MODERATE / HIGH / CRITICAL |

### Risk Rules

- **Equity > 80%** → Risk = HIGH (mandatory override)
- **Gold allocation** → Reduces risk score by up to 15%
- **< 3 asset types** → Diversification penalty
- **Crypto > 20%** → Elevated volatility warning

## Redis Caching

| Prefix | TTL | Purpose |
|--------|-----|---------|
| `market:` | 5 min | Individual asset market data |
| `analytics:` | 10 min | Trend, volatility, sector results |
| `risk:` | 10 min | Portfolio risk assessments |

## Database Tables

| Table | Description |
|-------|-------------|
| `market_data` | Point-in-time price snapshots with change %, volume |
| `sector_data` | Sector-level performance, weight, volatility |
| `risk_metrics` | Computed risk intelligence per portfolio (JSONB) |

## Local Development

```bash
cd market-service
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Requires PostgreSQL and Redis running
uvicorn app.main:app --reload --port 8001
```

## Docker

```bash
# From project root
docker-compose up --build market-service redis postgres
```

| Service | URL |
|---------|-----|
| Market API | http://localhost:8001 |
| Swagger | http://localhost:8001/docs |
| Health | http://localhost:8001/health |

## Seed Data

The service automatically seeds 90 days of market data (19 assets × 91 days = 1,729 records) and 10 sector records on first startup.
