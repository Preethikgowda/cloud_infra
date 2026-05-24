"""
IntelliWealth – AI Insight Service
Core orchestration layer that connects schemas → prompts → providers → responses.

IMPORTANT: AI does NOT give investment advice.
AI ONLY explains portfolio state and risk factors.
"""

import logging
import time
from typing import Dict

from app.config import get_settings
from app.providers.base import LLMProvider, LLMRequest
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.schemas.risk_summary import RiskSummaryRequest, RiskSummaryResponse
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.schemas.explain import ExplainRequest, ExplainResponse

logger = logging.getLogger("intelliwealth.ai.service")
settings = get_settings()

# Compliance system prompt enforced on all LLM requests
SYSTEM_PROMPT = (
    "You are IntelliWealth AI, a portfolio intelligence assistant.\n\n"
    "RULES:\n"
    "1. You EXPLAIN portfolio composition, risk factors, and market conditions.\n"
    "2. You NEVER provide investment advice, buy/sell recommendations, or price predictions.\n"
    "3. You always note that analysis does not constitute financial advice.\n"
    "4. Use precise data-driven language with specific numbers.\n"
    "5. Format responses in clear markdown.\n"
    "6. Be objective and factual."
)


class AIInsightService:
    """
    Orchestrates AI insight generation by:
    1. Receiving structured request data
    2. Building prompts with portfolio context
    3. Routing to the active LLM provider
    4. Returning structured responses with disclaimers
    """

    # ---- Metrics ----
    _request_count: int = 0
    _total_tokens: int = 0
    _total_latency_ms: float = 0.0
    _error_count: int = 0

    # ================================================================
    # POST /ai/analyze
    # ================================================================

    async def analyze_portfolio(
        self,
        request: AnalyzeRequest,
        provider: LLMProvider,
    ) -> AnalyzeResponse:
        """Generate comprehensive portfolio analysis."""
        self._request_count += 1
        logger.info("Analyze request for portfolio %s", request.portfolio_id)

        prompt = (
            f"Analyze the following investment portfolio:\n\n"
            f"Total Value: ${request.total_value:,.2f}\n"
            f"Risk Level: {request.risk_level}\n"
            f"Asset Count: {request.asset_count}\n"
            f"Allocation:\n"
        )
        for asset_type, pct in sorted(request.allocation.items(), key=lambda x: x[1], reverse=True):
            prompt += f"  - {asset_type}: {pct:.1f}%\n"

        prompt += (
            f"\nProvide a detailed analysis of the portfolio composition, "
            f"concentration characteristics, and risk profile. "
            f"Do NOT provide investment advice."
        )

        llm_request = LLMRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            metadata={
                "request_type": "analyze",
                "allocation": request.allocation,
                "total_value": request.total_value,
                "risk_level": request.risk_level,
                "asset_count": request.asset_count,
            },
        )

        llm_response = await provider.generate(llm_request)
        self._track_metrics(llm_response.tokens_used, llm_response.latency_ms)

        return AnalyzeResponse(
            portfolio_id=request.portfolio_id,
            analysis=llm_response.content,
            provider=llm_response.provider,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            latency_ms=llm_response.latency_ms,
            disclaimer=settings.DISCLAIMER,
        )

    # ================================================================
    # POST /ai/risk-summary
    # ================================================================

    async def generate_risk_summary(
        self,
        request: RiskSummaryRequest,
        provider: LLMProvider,
    ) -> RiskSummaryResponse:
        """Generate risk narration from risk engine data."""
        self._request_count += 1
        logger.info("Risk summary for portfolio %s (level=%s)", request.portfolio_id, request.risk_level)

        prompt = (
            f"Generate a risk intelligence summary for this portfolio:\n\n"
            f"Risk Score: {request.risk_score}/100\n"
            f"Risk Level: {request.risk_level}\n"
            f"Concentration Score: {request.concentration_score}/100\n"
            f"Diversification Score: {request.diversification_score}/100\n"
            f"Portfolio Volatility: {request.volatility}% annualized\n"
            f"Total Value: ${request.total_value:,.2f}\n"
            f"Allocation:\n"
        )
        for asset_type, pct in sorted(request.allocation.items(), key=lambda x: x[1], reverse=True):
            prompt += f"  - {asset_type}: {pct:.1f}%\n"

        prompt += (
            f"\nExplain what these risk metrics mean for the portfolio. "
            f"Highlight any concerning patterns. Do NOT advise on what to buy or sell."
        )

        llm_request = LLMRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            metadata={
                "request_type": "risk_summary",
                "allocation": request.allocation,
                "risk_score": request.risk_score,
                "risk_level": request.risk_level,
                "concentration_score": request.concentration_score,
                "diversification_score": request.diversification_score,
                "volatility": request.volatility,
                "total_value": request.total_value,
            },
        )

        llm_response = await provider.generate(llm_request)
        self._track_metrics(llm_response.tokens_used, llm_response.latency_ms)

        return RiskSummaryResponse(
            portfolio_id=request.portfolio_id,
            summary=llm_response.content,
            risk_level=request.risk_level,
            provider=llm_response.provider,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            latency_ms=llm_response.latency_ms,
            disclaimer=settings.DISCLAIMER,
        )

    # ================================================================
    # POST /ai/scenario-analysis
    # ================================================================

    async def run_scenario_analysis(
        self,
        request: ScenarioRequest,
        provider: LLMProvider,
    ) -> ScenarioResponse:
        """Generate scenario impact analysis."""
        self._request_count += 1
        logger.info("Scenario '%s' for portfolio %s", request.scenario_type, request.portfolio_id)

        prompt = (
            f"Perform a scenario analysis for a '{request.scenario_type}' event:\n\n"
            f"Portfolio Value: ${request.total_value:,.2f}\n"
            f"Current Risk Level: {request.risk_level}\n"
            f"Allocation:\n"
        )
        for asset_type, pct in sorted(request.allocation.items(), key=lambda x: x[1], reverse=True):
            prompt += f"  - {asset_type}: {pct:.1f}%\n"

        prompt += (
            f"\nProject the impact of a {request.scenario_type} scenario on each asset class. "
            f"Show estimated portfolio-level impact. "
            f"Base on historical correlations, not predictions. "
            f"Do NOT advise on actions to take."
        )

        llm_request = LLMRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            metadata={
                "request_type": "scenario_analysis",
                "scenario_type": request.scenario_type,
                "allocation": request.allocation,
                "total_value": request.total_value,
                "risk_level": request.risk_level,
            },
        )

        llm_response = await provider.generate(llm_request)
        self._track_metrics(llm_response.tokens_used, llm_response.latency_ms)

        return ScenarioResponse(
            portfolio_id=request.portfolio_id,
            scenario_type=request.scenario_type,
            analysis=llm_response.content,
            provider=llm_response.provider,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            latency_ms=llm_response.latency_ms,
            disclaimer=settings.DISCLAIMER,
        )

    # ================================================================
    # POST /ai/explain-portfolio
    # ================================================================

    async def explain_portfolio(
        self,
        request: ExplainRequest,
        provider: LLMProvider,
    ) -> ExplainResponse:
        """Generate plain-language portfolio explanation."""
        self._request_count += 1
        logger.info("Explain portfolio %s", request.portfolio_id)

        prompt = (
            f"Explain this investment portfolio in simple, non-technical language:\n\n"
            f"Total Value: ${request.total_value:,.2f}\n"
            f"Number of Assets: {request.asset_count}\n"
            f"Risk Level: {request.risk_level}\n"
            f"Allocation:\n"
        )
        for asset_type, pct in sorted(request.allocation.items(), key=lambda x: x[1], reverse=True):
            prompt += f"  - {asset_type}: {pct:.1f}%\n"

        prompt += (
            f"\nExplain what each asset type means and what the overall composition "
            f"tells us about the portfolio's behavior. Use everyday language. "
            f"Do NOT recommend any changes or provide investment advice."
        )

        llm_request = LLMRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            max_tokens=settings.LLM_MAX_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
            metadata={
                "request_type": "explain_portfolio",
                "allocation": request.allocation,
                "total_value": request.total_value,
                "asset_count": request.asset_count,
                "risk_level": request.risk_level,
            },
        )

        llm_response = await provider.generate(llm_request)
        self._track_metrics(llm_response.tokens_used, llm_response.latency_ms)

        return ExplainResponse(
            portfolio_id=request.portfolio_id,
            explanation=llm_response.content,
            provider=llm_response.provider,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            latency_ms=llm_response.latency_ms,
            disclaimer=settings.DISCLAIMER,
        )

    # ================================================================
    # Metrics
    # ================================================================

    def _track_metrics(self, tokens: int, latency_ms: float) -> None:
        self._total_tokens += tokens
        self._total_latency_ms += latency_ms

    def get_metrics(self) -> Dict:
        """Return service-level metrics."""
        avg_latency = (
            self._total_latency_ms / self._request_count
            if self._request_count > 0
            else 0.0
        )
        return {
            "total_requests": self._request_count,
            "total_tokens_used": self._total_tokens,
            "total_latency_ms": round(self._total_latency_ms, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "error_count": self._error_count,
        }
