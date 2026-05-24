# IntelliWealth – Future Roadmap

## Strategic Vision

IntelliWealth is designed to evolve from a portfolio management platform into a full **AI-powered wealth intelligence system**. The architecture is built with extensibility at its core — the LLM provider abstraction, dependency injection pattern, and microservices boundaries enable incremental adoption of advanced AI capabilities without rewriting business logic.

---

## Phase 6: AWS Bedrock Integration

### Objective
Replace the MockProvider with production-grade Claude models via AWS Bedrock for real-time, context-aware portfolio intelligence.

### Implementation Plan

```
Current State                    Target State
─────────────                    ────────────
LLM_PROVIDER=mock        →      LLM_PROVIDER=bedrock
MockProvider (templates)  →      BedrockProvider (Claude 3)
Local generation          →      AWS Bedrock API calls
```

### Steps

| Step | Task | Effort | Dependencies |
|------|------|--------|--------------|
| 6.1 | Configure AWS IAM role for Bedrock access | 1 day | AWS account |
| 6.2 | Enable Claude 3 Haiku model in Bedrock console | 1 hour | AWS approval |
| 6.3 | Set K8s secrets with AWS credentials | 1 hour | IAM role |
| 6.4 | Update ConfigMap: `LLM_PROVIDER=bedrock` | 5 min | — |
| 6.5 | Rolling restart of AI Insight Service | 5 min | — |
| 6.6 | Validate response quality with test portfolios | 1 day | Test data |
| 6.7 | Monitor token usage and latency via Grafana | Ongoing | — |

### Bedrock Model Options

| Model | Latency | Token Cost | Best For |
|-------|---------|------------|----------|
| Claude 3 Haiku | ~1s | Lowest | High-volume analysis |
| Claude 3 Sonnet | ~3s | Medium | Detailed narratives |
| Claude 3.5 Sonnet | ~3s | Medium | Complex scenarios |
| Claude 3 Opus | ~8s | Highest | Deep research analysis |
| Amazon Titan | ~2s | Low | Cost optimization |

### Cost Estimation

| Metric | Estimate |
|--------|----------|
| Avg tokens per request | ~800 |
| Requests per day (initial) | ~1,000 |
| Daily token consumption | ~800K |
| Monthly cost (Haiku) | ~$15–25 |
| Monthly cost (Sonnet) | ~$75–120 |

### Configuration Change

```yaml
# k8s/base/ai-insight-service/configmap.yaml
data:
  LLM_PROVIDER: "bedrock"                           # ← Change this
  BEDROCK_MODEL_ID: "anthropic.claude-3-haiku-20240307-v1:0"
```

### Zero-Downtime Activation

The provider switch requires **zero code changes**:

```bash
# Update ConfigMap
kubectl apply -f k8s/base/ai-insight-service/configmap.yaml

# Rolling restart
kubectl rollout restart deployment/ai-insight-service -n intelliwealth

# Verify
kubectl logs -l app=ai-insight-service -n intelliwealth | grep "Bedrock"
```

---

## Phase 7: LangChain Integration

### Objective
Implement structured LangChain pipelines for advanced prompt engineering, output parsing, and retrieval-augmented generation.

### Architecture

```
                    ┌──────────────────────────────────────┐
                    │        LangChain Pipeline            │
                    │                                      │
 User Request ─────▶  Prompt Template                     │
                    │       │                              │
                    │       ▼                              │
                    │  Output Parser                       │
                    │       │                              │
                    │       ▼                              │
                    │  LLM Chain (Bedrock)                 │
                    │       │                              │
                    │       ▼                              │
                    │  Structured Response                 │
                    └──────────────────────────────────────┘
```

### Planned Chains

| Chain | Input | Output | Purpose |
|-------|-------|--------|---------|
| `PortfolioAnalysisChain` | Allocation + risk data | Structured markdown | Deep composition analysis |
| `RiskNarrationChain` | Risk metrics | Tiered risk report | Multi-level risk explanation |
| `ScenarioChain` | Allocation + scenario type | Impact table + narrative | What-if projection |
| `ComplianceChain` | AI output | Validated output | Filter investment advice |

### Output Parsers

```python
from langchain_core.output_parsers import PydanticOutputParser

class PortfolioInsight(BaseModel):
    summary: str
    risk_factors: List[str]
    key_observations: List[str]
    sector_analysis: Dict[str, str]

parser = PydanticOutputParser(pydantic_object=PortfolioInsight)
```

### Prompt Templates

```python
from langchain_core.prompts import ChatPromptTemplate

analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", COMPLIANCE_PROMPT),
    ("human", """
    Analyze this portfolio:
    Total Value: {total_value}
    Allocation: {allocation}
    Risk Level: {risk_level}

    {format_instructions}
    """),
])
```

### Implementation Steps

| Step | Task | Effort |
|------|------|--------|
| 7.1 | Create `app/chains/` directory | 1 day |
| 7.2 | Implement `PortfolioAnalysisChain` | 2 days |
| 7.3 | Add Pydantic output parsers | 1 day |
| 7.4 | Integrate compliance validation chain | 1 day |
| 7.5 | Replace direct provider calls with chains | 2 days |
| 7.6 | Add chain-level metrics and tracing | 1 day |

---

## Phase 8: RAG Pipeline (Retrieval-Augmented Generation)

### Objective
Enable the AI to reference historical portfolio data, market reports, and risk assessments when generating insights — producing more accurate, context-aware analysis.

### Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           RAG Pipeline                   │
                    │                                         │
 Portfolio Data ───▶│  Document Loader                        │
                    │       │                                 │
 Market Reports ───▶│       ▼                                 │
                    │  Text Splitter (RecursiveCharacter)      │
 Risk History ─────▶│       │                                 │
                    │       ▼                                 │
                    │  Embedding Model (Titan / OpenAI)       │
                    │       │                                 │
                    │       ▼                                 │
                    │  Vector Store (pgvector / FAISS)        │
                    │       │                                 │
                    │       ▼                                 │
                    │  Retriever (k=5, similarity)            │
                    │       │                                 │
                    │       ▼                                 │
                    │  LLM Chain (Bedrock Claude)             │
                    │       │                                 │
                    │       ▼                                 │
                    │  Context-Aware Response                 │
                    └─────────────────────────────────────────┘
```

### Data Sources for RAG

| Source | Type | Update Frequency |
|--------|------|------------------|
| Portfolio history snapshots | Structured | On portfolio change |
| Risk assessment history | Structured | On risk computation |
| Market sector reports | Semi-structured | Daily |
| Asset price trends | Time-series | Hourly |

### Vector Store Options

| Option | Pros | Cons |
|--------|------|------|
| **pgvector** (PostgreSQL extension) | Reuse existing DB, simple | Limited scale |
| **FAISS** (in-memory) | Fast, no infra | Ephemeral |
| **Amazon OpenSearch** | Managed, scalable | Cost, complexity |
| **Pinecone** | Managed, fast | External dependency |

### Implementation Steps

| Step | Task | Effort |
|------|------|--------|
| 8.1 | Add pgvector extension to PostgreSQL | 1 day |
| 8.2 | Create embedding pipeline for portfolio data | 3 days |
| 8.3 | Implement retriever with similarity search | 2 days |
| 8.4 | Integrate with `generate_with_context()` | 2 days |
| 8.5 | Create scheduled embedding refresh job | 2 days |

---

## Phase 9: AI Agents

### Objective
Implement autonomous AI agents that can orchestrate multi-step analysis workflows, pulling data from multiple services to answer complex portfolio questions.

### Agent Architecture

```
                    ┌─────────────────────────────────────────┐
                    │          AI Agent Orchestrator           │
                    │                                         │
 User Question ────▶│  Agent (ReAct / Plan-and-Execute)      │
                    │       │                                 │
                    │       ▼                                 │
                    │  ┌─────────────────────────────────┐   │
                    │  │         Tool Selection           │   │
                    │  │                                   │   │
                    │  │  ┌──────────┐  ┌──────────────┐ │   │
                    │  │  │Portfolio │  │Market Data   │ │   │
                    │  │  │Tool      │  │Tool          │ │   │
                    │  │  └──────────┘  └──────────────┘ │   │
                    │  │  ┌──────────┐  ┌──────────────┐ │   │
                    │  │  │Risk      │  │Scenario      │ │   │
                    │  │  │Tool      │  │Tool          │ │   │
                    │  │  └──────────┘  └──────────────┘ │   │
                    │  │  ┌──────────┐                    │   │
                    │  │  │History   │                    │   │
                    │  │  │Tool      │                    │   │
                    │  │  └──────────┘                    │   │
                    │  └─────────────────────────────────┘   │
                    │       │                                 │
                    │       ▼                                 │
                    │  Multi-step reasoning + tool calls      │
                    │       │                                 │
                    │       ▼                                 │
                    │  Comprehensive analysis report          │
                    └─────────────────────────────────────────┘
```

### Agent Tools

| Tool | Service | Action |
|------|---------|--------|
| `get_portfolio` | Portfolio Service | Fetch portfolio + assets |
| `get_allocation` | Portfolio Service | Compute allocation breakdown |
| `get_market_data` | Market Service | Fetch latest asset prices |
| `get_risk_assessment` | Market Service | Run risk engine |
| `get_sector_analysis` | Market Service | Sector performance |
| `run_scenario` | AI Service | Project scenario impact |
| `get_history` | Portfolio Service | Historical snapshots |

### Example Agent Interaction

**User:** "How would my portfolio perform if we enter a recession, and what changes in allocation would reduce my risk?"

**Agent reasoning:**
```
Thought: I need to understand the current portfolio, assess risk, and run a recession scenario.

Action 1: get_portfolio(id="550e8400-...")
Observation: Portfolio has 5 assets, $250K total, 85% equity

Action 2: get_risk_assessment(portfolio_id="550e8400-...")
Observation: Risk level HIGH, concentration 65, diversification 35

Action 3: run_scenario(scenario_type="recession", allocation={...})
Observation: Projected loss -28.5% ($-71,250)

Action 4: [Synthesize analysis]
Final Answer: "Your portfolio would experience an estimated 28.5% drawdown
in a recession scenario. The high equity concentration (85%) is the primary
risk driver. Note: This analysis explains portfolio behavior — it does not
constitute investment advice."
```

### Implementation Steps

| Step | Task | Effort |
|------|------|--------|
| 9.1 | Create `app/agents/` directory with tool definitions | 3 days |
| 9.2 | Implement LangChain tools wrapping service APIs | 3 days |
| 9.3 | Create ReAct agent with compliance guardrails | 3 days |
| 9.4 | Add agent endpoint `POST /api/v1/ai/agent-query` | 1 day |
| 9.5 | Implement conversation memory (Redis-backed) | 2 days |
| 9.6 | Add agent-level metrics and cost tracking | 2 days |

---

## Timeline Summary

```
Phase 6: Bedrock          ███░░░░░░░░░░░░  ~3 days
Phase 7: LangChain        █████░░░░░░░░░░  ~8 days
Phase 8: RAG              ███████░░░░░░░░  ~10 days
Phase 9: Agents           █████████░░░░░░  ~14 days
                          ─────────────────
                          Total: ~35 days
```

| Phase | Duration | Prerequisites | Risk |
|-------|----------|---------------|------|
| 6. Bedrock | 3 days | AWS account, IAM role | Low — code ready |
| 7. LangChain | 8 days | Phase 6 | Low — deps installed |
| 8. RAG | 10 days | Phase 7 | Medium — new infra |
| 9. Agents | 14 days | Phase 7 + 8 | Medium — complexity |

---

## Compliance Guardrails (All Phases)

Every phase must maintain the core compliance rule:

> **AI does NOT provide investment advice. AI ONLY explains portfolio state and risk factors.**

| Guardrail | Implementation |
|-----------|---------------|
| System prompt enforcement | Every LLM call includes compliance instructions |
| Output validation | ComplianceChain filters advisory language |
| Disclaimer injection | Every response includes mandatory disclaimer |
| Agent tool restrictions | Tools are read-only — no trade execution |
| Audit logging | All AI interactions logged with full context |
