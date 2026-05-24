"""
IntelliWealth – AI Insight Service Configuration
Centralized configuration with provider selection and AWS/Bedrock readiness.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- Application ----
    APP_NAME: str = "IntelliWealth AI Insight Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # ---- Server ----
    AI_SERVICE_HOST: str = "0.0.0.0"
    AI_SERVICE_PORT: int = 8002
    AI_SERVICE_LOG_LEVEL: str = "info"
    AI_SERVICE_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8000"

    # ---- LLM Provider ----
    LLM_PROVIDER: str = "mock"  # Options: mock, bedrock
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE: float = 0.3

    # ---- AWS Bedrock (prepared) ----
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"

    # ---- Internal Service URLs ----
    PORTFOLIO_SERVICE_URL: str = "http://portfolio-service:8000"
    MARKET_SERVICE_URL: str = "http://market-service:8001"

    # ---- LangChain (prepared) ----
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None

    # ---- Rate Limiting ----
    AI_MAX_REQUESTS_PER_MINUTE: int = 30

    # ---- Compliance ----
    DISCLAIMER: str = (
        "DISCLAIMER: This analysis explains portfolio composition and risk factors. "
        "It does NOT constitute investment advice. Always consult a qualified financial "
        "advisor before making investment decisions."
    )

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.AI_SERVICE_CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
