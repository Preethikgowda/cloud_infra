"""
IntelliWealth – AI Service Dependency Injection
Provides LLM provider instances via FastAPI's Depends() system.
"""

import logging
from functools import lru_cache

from app.config import get_settings
from app.providers.base import LLMProvider
from app.providers.mock_provider import MockProvider
from app.providers.bedrock_provider import BedrockProvider

logger = logging.getLogger("intelliwealth.ai.di")
settings = get_settings()


@lru_cache()
def _create_provider() -> LLMProvider:
    """
    Factory function that creates the appropriate LLM provider
    based on the LLM_PROVIDER environment variable.

    Returns a cached singleton instance.
    """
    provider_name = settings.LLM_PROVIDER.lower()

    if provider_name == "bedrock":
        logger.info("Initializing AWS Bedrock provider (model=%s)", settings.BEDROCK_MODEL_ID)
        return BedrockProvider()
    elif provider_name == "mock":
        logger.info("Initializing Mock provider for development")
        return MockProvider()
    else:
        logger.warning("Unknown provider '%s', falling back to MockProvider", provider_name)
        return MockProvider()


def get_llm_provider() -> LLMProvider:
    """
    FastAPI dependency that returns the active LLM provider.

    Usage:
        @router.post("/endpoint")
        async def handler(provider: LLMProvider = Depends(get_llm_provider)):
            response = await provider.generate(request)
    """
    return _create_provider()
