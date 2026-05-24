# IntelliWealth – AI Insight Service

Enterprise-grade AI-powered portfolio intelligence and narration engine.

> **IMPORTANT: This service does NOT provide investment advice.**
> It ONLY explains portfolio state, risk factors, and market conditions.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  AI INSIGHT SERVICE                          │
│                  FastAPI / Port 8002                         │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    API Layer                          │   │
│  │  POST /ai/analyze        POST /ai/risk-summary       │   │
│  │  POST /ai/scenario-analysis   POST /ai/explain       │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │               AI Service (Orchestrator)               │   │
│  │  - Builds structured prompts                          │   │
│  │  - Enforces compliance rules                          │   │
│  │  - Tracks metrics                                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │ Dependency Injection                   │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │            LLMProvider Interface (ABC)                │   │
│  │                                                       │   │
│  │  ┌─────────────────┐    ┌─────────────────────────┐  │   │
│  │  │  MockProvider    │    │  BedrockProvider        │  │   │
│  │  │  (Active)        │    │  (Prepared)             │  │   │
│  │  │  Template-based  │    │  Claude / Titan         │  │   │
│  │  └─────────────────┘    └─────────────────────────┘  │   │
│  │                                                       │   │
│  │  Future: LangChain agents, RAG pipelines              │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/ai/analyze` | Portfolio composition analysis |
| POST | `/api/v1/ai/risk-summary` | Risk narration from metrics |
| POST | `/api/v1/ai/scenario-analysis` | What-if scenario projection |
| POST | `/api/v1/ai/explain-portfolio` | Plain-language explanation |
| GET | `/health` | Health check |
| GET | `/readiness` | LLM provider readiness |
| GET | `/liveness` | Process alive |
| GET | `/metrics` | Operational metrics |

## Provider Pattern

The service uses an **interface-based provider abstraction**:

```python
class LLMProvider(ABC):
    async def generate(request: LLMRequest) -> LLMResponse
    async def health_check() -> Dict
    async def generate_with_context(request, context_docs) -> LLMResponse  # RAG-ready
```

### Available Providers

| Provider | Status | Use Case |
|----------|--------|----------|
| `MockProvider` | ✅ Active | Development & testing |
| `BedrockProvider` | 🔧 Prepared | Production (AWS Bedrock) |

### Switching Providers

```bash
# Use mock (default)
LLM_PROVIDER=mock

# Use AWS Bedrock
LLM_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

## Compliance

Every response includes a mandatory disclaimer:

> *DISCLAIMER: This analysis explains portfolio composition and risk factors.
> It does NOT constitute investment advice. Always consult a qualified
> financial advisor before making investment decisions.*

The compliance system prompt enforces:
1. AI **EXPLAINS** portfolio state — never advises
2. No buy/sell recommendations
3. No price predictions
4. Data-driven, objective language

## Scenario Types

| Scenario | Equity | Bonds | Gold | Crypto |
|----------|--------|-------|------|--------|
| `market_correction` | -20% | +3% | +8% | -35% |
| `recession` | -35% | +8% | +15% | -50% |
| `inflation_surge` | -8% | -12% | +20% | -5% |
| `bull_market` | +30% | -2% | -5% | +60% |

## Future Readiness

The architecture is prepared for:

- **RAG Pipelines**: `generate_with_context()` method accepts retrieval documents
- **LangChain Agents**: Dependencies installed, agent pattern ready
- **AWS Bedrock**: Full client implementation with Claude message format
- **Custom Models**: Interface pattern allows any provider implementation

## Local Development

```bash
cd ai-insight-service
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8002
```

## Docker

```bash
docker-compose up --build ai-insight-service
```

| Service | URL |
|---------|-----|
| AI API | http://localhost:8002 |
| Swagger | http://localhost:8002/docs |
| Health | http://localhost:8002/health |
| Metrics | http://localhost:8002/metrics |

## Example Request

```bash
curl -X POST http://localhost:8002/api/v1/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": "550e8400-e29b-41d4-a716-446655440000",
    "allocation": {"stocks": 90, "bonds": 5, "cash": 5},
    "total_value": 250000,
    "risk_level": "HIGH",
    "asset_count": 12
  }'
```

**Response excerpt:**
> *Portfolio highly depends on equity exposure. With 90% in stocks and
> equity funds, your returns will closely track the stock market...*
