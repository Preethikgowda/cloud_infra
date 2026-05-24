# IntelliWealth – Complete API Documentation

## Base URLs

| Environment | Portfolio Service | Market Service | AI Insight Service |
|-------------|-------------------|----------------|---------------------|
| Local | http://localhost:8000 | http://localhost:8001 | http://localhost:8002 |
| Production | https://{domain}/api/v1 | https://{domain}/api/v1/market | https://{domain}/api/v1/ai |

All services expose interactive API documentation:
- **Swagger UI**: `{base_url}/docs`
- **ReDoc**: `{base_url}/redoc`
- **OpenAPI JSON**: `{base_url}/openapi.json`

---

## Portfolio Service (Port 8000)

### Authentication

#### POST `/api/v1/auth/login`
Authenticate a customer and receive JWT tokens.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/api/v1/auth/refresh`
Refresh an expired access token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

---

### Customers

#### POST `/api/v1/customers`
Create a new customer account.

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "phone": "+1-555-0100"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+1-555-0100",
  "is_active": true,
  "created_at": "2026-05-24T06:30:00Z"
}
```

#### GET `/api/v1/customers/{id}`
**Auth:** Bearer token required.

#### PUT `/api/v1/customers/{id}`
**Auth:** Bearer token required.

#### GET `/api/v1/customers`
**Auth:** Admin role required.

---

### Portfolios

#### POST `/api/v1/portfolio`
Create a new portfolio.

**Auth:** Bearer token required.

**Request:**
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Growth Portfolio",
  "description": "Long-term growth strategy"
}
```

#### GET `/api/v1/portfolio/{id}`
Get portfolio with all assets.

**Auth:** Bearer token required.

#### POST `/api/v1/portfolio/add-asset`
Add an asset to a portfolio.

**Auth:** Bearer token required.

**Request:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "asset_name": "Apple Inc.",
  "asset_type": "stocks",
  "quantity": 100,
  "purchase_price": 175.50,
  "current_value": 19250.00
}
```

**Valid `asset_type` values:** `stocks`, `mutual_funds`, `bonds`, `gold`, `crypto`, `cash`

#### PUT `/api/v1/portfolio/update-asset/{id}`
**Auth:** Bearer token required.

#### DELETE `/api/v1/portfolio/remove-asset/{id}`
**Auth:** Bearer token required.

#### GET `/api/v1/portfolio/allocation/{id}`
Get asset allocation breakdown.

**Auth:** Bearer token required.

**Response (200):**
```json
{
  "portfolio_id": "550e8400-...",
  "total_value": 250000.00,
  "allocation": {
    "stocks": 60.0,
    "bonds": 20.0,
    "gold": 10.0,
    "crypto": 5.0,
    "cash": 5.0
  },
  "asset_count": 12
}
```

#### GET `/api/v1/portfolio/history/{id}`
**Auth:** Bearer token required.

---

## Market Intelligence Service (Port 8001)

### GET `/api/v1/market/assets`
Latest market data for tracked assets.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `asset_type` | string | — | Filter by type |
| `limit` | int | 20 | Max results |
| `offset` | int | 0 | Pagination offset |

**Response (200):**
```json
{
  "assets": [
    {
      "id": "...",
      "asset_name": "AAPL",
      "asset_type": "stocks",
      "price": 198.50,
      "previous_price": 195.20,
      "change_percent": 1.69,
      "volume": 45000000,
      "market_cap": 3050000000000,
      "timestamp": "2026-05-24T06:00:00Z"
    }
  ],
  "total": 19,
  "cached": false
}
```

### GET `/api/v1/market/trends`
Price trend analysis for an asset.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `asset_name` | string | required | Asset to analyze |
| `period` | string | `1M` | `1W`, `1M`, `3M`, `6M`, `1Y` |

### GET `/api/v1/market/volatility`
Market volatility metrics.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `asset_type` | string | — | Filter by type |

### GET `/api/v1/market/risk`
Full portfolio risk assessment.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `portfolio_id` | UUID | Portfolio to assess |

**Response (200):**
```json
{
  "portfolio_id": "550e8400-...",
  "risk_score": 62.5,
  "risk_level": "HIGH",
  "concentration_score": 45.0,
  "diversification_score": 38.0,
  "volatility": 16.8,
  "sector_exposure": {
    "Equity": 85.0,
    "Fixed Income": 10.0,
    "Commodities": 5.0
  },
  "concentration_breakdown": [
    { "asset_type": "stocks", "allocation_percent": 85.0, "risk_contribution": "high" }
  ],
  "recommendations": [
    "CRITICAL: Equity allocation at 85.0% exceeds the 80% threshold..."
  ],
  "computed_at": "2026-05-24T06:30:00Z"
}
```

### GET `/api/v1/market/sector-analysis`
Sector performance report.

---

## AI Insight Service (Port 8002)

> **Compliance:** All AI responses include a mandatory disclaimer. The AI explains portfolio state — it never provides investment advice.

### POST `/api/v1/ai/analyze`
Portfolio composition analysis.

**Request:**
```json
{
  "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
  "allocation": { "stocks": 90.0, "bonds": 5.0, "cash": 5.0 },
  "total_value": 250000.00,
  "risk_level": "HIGH",
  "asset_count": 12
}
```

**Response (200):**
```json
{
  "portfolio_id": "550e8400-...",
  "analysis": "## Portfolio Analysis\n\nThe portfolio has a total estimated value of $250,000.00...\n\n### Equity Concentration\n\nEquity instruments represent **90.0%** of the portfolio. This level of equity concentration exceeds the 80% threshold...",
  "provider": "IntelliWealth Mock Provider",
  "model": "mock-analyst-v1",
  "tokens_used": 187,
  "latency_ms": 2.5,
  "disclaimer": "DISCLAIMER: This analysis explains portfolio composition..."
}
```

### POST `/api/v1/ai/risk-summary`
Risk narration from risk engine metrics.

**Request:**
```json
{
  "portfolio_id": "550e8400-...",
  "allocation": { "stocks": 60.0, "bonds": 20.0, "gold": 10.0, "crypto": 5.0, "cash": 5.0 },
  "risk_score": 42.5,
  "risk_level": "MODERATE",
  "concentration_score": 30.0,
  "diversification_score": 65.0,
  "volatility": 14.2,
  "total_value": 500000.00
}
```

### POST `/api/v1/ai/scenario-analysis`
What-if scenario projection.

**Request:**
```json
{
  "portfolio_id": "550e8400-...",
  "allocation": { "stocks": 60.0, "bonds": 20.0, "gold": 10.0, "crypto": 5.0, "cash": 5.0 },
  "total_value": 500000.00,
  "scenario_type": "market_correction"
}
```

**Valid `scenario_type` values:** `market_correction`, `recession`, `inflation_surge`, `bull_market`

### POST `/api/v1/ai/explain-portfolio`
Plain-language portfolio explanation.

---

## Health Endpoints (All Services)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic health check |
| GET | `/readiness` | Dependency readiness (DB, Redis, LLM) |
| GET | `/liveness` | Process alive check |
| GET | `/metrics` | Prometheus metrics (text format) |

---

## Error Responses

All services return consistent error format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request / validation error |
| 401 | Authentication required |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 422 | Validation error (Pydantic) |
| 500 | Internal server error |

---

## Response Headers

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Unique request identifier |
| `X-Correlation-ID` | Distributed trace identifier |
| `X-Process-Time-Ms` | Server processing time |
