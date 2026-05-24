"""
IntelliWealth – Analyze Endpoint Schemas
"""

from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for POST /ai/analyze."""
    portfolio_id: UUID = Field(..., description="Portfolio ID to analyze")
    allocation: Dict[str, float] = Field(
        ...,
        description="Asset allocation map, e.g. {'stocks': 60.0, 'bonds': 20.0, 'gold': 10.0}",
        examples=[{"stocks": 60.0, "bonds": 20.0, "gold": 10.0, "crypto": 5.0, "cash": 5.0}],
    )
    total_value: float = Field(..., ge=0, description="Total portfolio value in USD")
    risk_level: Optional[str] = Field("MODERATE", description="Current risk level classification")
    asset_count: Optional[int] = Field(0, ge=0, description="Number of individual assets")


class AnalyzeResponse(BaseModel):
    """Response body for POST /ai/analyze."""
    portfolio_id: UUID
    analysis: str = Field(..., description="AI-generated portfolio analysis narrative")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model identifier")
    tokens_used: int = 0
    latency_ms: float = 0.0
    disclaimer: str
