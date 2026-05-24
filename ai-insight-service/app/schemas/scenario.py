"""
IntelliWealth – Scenario Analysis Endpoint Schemas
"""

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScenarioRequest(BaseModel):
    """Request body for POST /ai/scenario-analysis."""
    portfolio_id: UUID = Field(..., description="Portfolio ID")
    allocation: Dict[str, float] = Field(..., description="Asset allocation map")
    total_value: float = Field(..., ge=0, description="Total portfolio value in USD")
    scenario_type: str = Field(
        "market_correction",
        description="Scenario type: market_correction, recession, inflation_surge, bull_market",
    )
    risk_level: Optional[str] = Field("MODERATE", description="Current risk level")


class ScenarioResponse(BaseModel):
    """Response body for POST /ai/scenario-analysis."""
    portfolio_id: UUID
    scenario_type: str
    analysis: str = Field(..., description="AI-generated scenario impact analysis")
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    disclaimer: str
