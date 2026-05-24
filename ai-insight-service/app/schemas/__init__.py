"""IntelliWealth – AI Insight Schemas Package"""

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.schemas.risk_summary import RiskSummaryRequest, RiskSummaryResponse
from app.schemas.scenario import ScenarioRequest, ScenarioResponse
from app.schemas.explain import ExplainRequest, ExplainResponse

__all__ = [
    "AnalyzeRequest", "AnalyzeResponse",
    "RiskSummaryRequest", "RiskSummaryResponse",
    "ScenarioRequest", "ScenarioResponse",
    "ExplainRequest", "ExplainResponse",
]
