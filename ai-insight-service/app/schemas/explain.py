"""
IntelliWealth – Explain Portfolio Endpoint Schemas
"""

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExplainRequest(BaseModel):
    """Request body for POST /ai/explain-portfolio."""
    portfolio_id: UUID = Field(..., description="Portfolio ID")
    allocation: Dict[str, float] = Field(..., description="Asset allocation map")
    total_value: float = Field(..., ge=0, description="Total portfolio value")
    asset_count: int = Field(0, ge=0, description="Number of individual assets")
    risk_level: Optional[str] = Field("MODERATE", description="Risk level classification")


class ExplainResponse(BaseModel):
    """Response body for POST /ai/explain-portfolio."""
    portfolio_id: UUID
    explanation: str = Field(..., description="Plain-language portfolio explanation")
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    disclaimer: str
