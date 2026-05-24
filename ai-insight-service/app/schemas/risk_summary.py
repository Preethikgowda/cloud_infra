"""
IntelliWealth – Risk Summary Endpoint Schemas
"""

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RiskSummaryRequest(BaseModel):
    """Request body for POST /ai/risk-summary."""
    portfolio_id: UUID = Field(..., description="Portfolio ID")
    allocation: Dict[str, float] = Field(..., description="Asset allocation map")
    risk_score: float = Field(..., ge=0, le=100, description="Risk score (0–100)")
    risk_level: str = Field(..., description="Risk level: LOW, MODERATE, HIGH, CRITICAL")
    concentration_score: float = Field(0, ge=0, le=100, description="Concentration score")
    diversification_score: float = Field(0, ge=0, le=100, description="Diversification score")
    volatility: float = Field(0, ge=0, description="Annualized portfolio volatility")
    total_value: Optional[float] = Field(0, ge=0, description="Total portfolio value")


class RiskSummaryResponse(BaseModel):
    """Response body for POST /ai/risk-summary."""
    portfolio_id: UUID
    summary: str = Field(..., description="AI-generated risk narration")
    risk_level: str
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    disclaimer: str
