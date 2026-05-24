"""
IntelliWealth – AI Insight Router
All AI analysis endpoints.

IMPORTANT: AI does NOT give investment advice.
AI ONLY explains portfolio state and risk factors.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.dependencies import get_llm_provider
from app.providers.base import LLMProvider
from app.routers.health import get_ai_service
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.schemas.risk_summary import RiskSummaryRequest, RiskSummaryResponse
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.ai_service import AIInsightService

logger = logging.getLogger("intelliwealth.ai.router")
router = APIRouter(prefix="/api/v1/ai", tags=["AI Insights"])
settings = get_settings()

VALID_SCENARIOS = {"market_correction", "recession", "inflation_surge", "bull_market"}


# ================================================================
# POST /ai/analyze
# ================================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze portfolio composition",
    description=(
        "Generate AI-powered analysis of portfolio composition and characteristics. "
        "Returns an analytical narrative explaining allocation, concentration, and risk profile. "
        "Does NOT provide investment advice."
    ),
)
async def analyze_portfolio(
    request: AnalyzeRequest,
    provider: LLMProvider = Depends(get_llm_provider),
    service: AIInsightService = Depends(get_ai_service),
):
    try:
        return await service.analyze_portfolio(request, provider)
    except Exception as exc:
        logger.error("Analyze failed for %s: %s", request.portfolio_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI analysis generation failed. Please try again.",
        )


# ================================================================
# POST /ai/risk-summary
# ================================================================

@router.post(
    "/risk-summary",
    response_model=RiskSummaryResponse,
    summary="Generate risk narration",
    description=(
        "Transform risk engine metrics into a human-readable risk narration. "
        "Explains what the risk score, concentration, and volatility mean. "
        "Does NOT recommend portfolio changes."
    ),
)
async def generate_risk_summary(
    request: RiskSummaryRequest,
    provider: LLMProvider = Depends(get_llm_provider),
    service: AIInsightService = Depends(get_ai_service),
):
    try:
        return await service.generate_risk_summary(request, provider)
    except Exception as exc:
        logger.error("Risk summary failed for %s: %s", request.portfolio_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Risk summary generation failed. Please try again.",
        )


# ================================================================
# POST /ai/scenario-analysis
# ================================================================

@router.post(
    "/scenario-analysis",
    response_model=ScenarioResponse,
    summary="Run scenario analysis",
    description=(
        "Project the impact of a hypothetical market event on the portfolio. "
        "Scenarios: market_correction, recession, inflation_surge, bull_market. "
        "Based on historical correlations, not predictions."
    ),
)
async def run_scenario_analysis(
    request: ScenarioRequest,
    provider: LLMProvider = Depends(get_llm_provider),
    service: AIInsightService = Depends(get_ai_service),
):
    if request.scenario_type not in VALID_SCENARIOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scenario '{request.scenario_type}'. Valid: {', '.join(VALID_SCENARIOS)}",
        )
    try:
        return await service.run_scenario_analysis(request, provider)
    except Exception as exc:
        logger.error("Scenario failed for %s: %s", request.portfolio_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scenario analysis generation failed. Please try again.",
        )


# ================================================================
# POST /ai/explain-portfolio
# ================================================================

@router.post(
    "/explain-portfolio",
    response_model=ExplainResponse,
    summary="Explain portfolio in plain language",
    description=(
        "Generate a clear, non-technical explanation of what the portfolio contains "
        "and what the current allocation means. Designed for investors who want "
        "to understand their holdings without financial jargon."
    ),
)
async def explain_portfolio(
    request: ExplainRequest,
    provider: LLMProvider = Depends(get_llm_provider),
    service: AIInsightService = Depends(get_ai_service),
):
    try:
        return await service.explain_portfolio(request, provider)
    except Exception as exc:
        logger.error("Explain failed for %s: %s", request.portfolio_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Portfolio explanation generation failed. Please try again.",
        )
