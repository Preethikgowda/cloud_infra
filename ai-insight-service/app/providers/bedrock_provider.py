"""
IntelliWealth – AWS Bedrock LLM Provider
Production-ready provider for Amazon Bedrock foundation models.

PREPARED but NOT ACTIVE until AWS credentials are configured.
Supports Claude, Titan, and other Bedrock-hosted models.

IMPORTANT: AI does NOT give investment advice.
AI ONLY explains portfolio state and risk factors.
"""

import json
import logging
import time
from typing import Any, Dict, List

from app.config import get_settings
from app.providers.base import LLMProvider, LLMRequest, LLMResponse

logger = logging.getLogger("intelliwealth.ai.bedrock")
settings = get_settings()

# System prompt enforcing compliance
SYSTEM_PROMPT = (
    "You are IntelliWealth AI, a portfolio intelligence assistant. "
    "You EXPLAIN portfolio composition, risk factors, and market conditions. "
    "You NEVER provide investment advice, buy/sell recommendations, or price predictions. "
    "You always include a disclaimer that your analysis does not constitute financial advice. "
    "Use data-driven language. Be precise with numbers. "
    "Format responses in clear markdown with sections."
)


class BedrockProvider(LLMProvider):
    """
    AWS Bedrock LLM provider using Claude or Titan models.

    Requires AWS credentials configured via environment variables:
    - AWS_REGION
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - BEDROCK_MODEL_ID
    """

    def __init__(self) -> None:
        self._client = None
        self._model_id = settings.BEDROCK_MODEL_ID
        self._initialized = False

    def _ensure_client(self):
        """Lazy-initialize Bedrock client."""
        if self._client is not None:
            return

        try:
            import boto3

            self._client = boto3.client(
                "bedrock-runtime",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            self._initialized = True
            logger.info(
                "Bedrock client initialized: region=%s model=%s",
                settings.AWS_REGION,
                self._model_id,
            )
        except Exception as exc:
            logger.error("Failed to initialize Bedrock client: %s", exc)
            raise RuntimeError(f"Bedrock initialization failed: {exc}")

    @property
    def provider_name(self) -> str:
        return "AWS Bedrock"

    @property
    def model_id(self) -> str:
        return self._model_id

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate completion via AWS Bedrock."""
        self._ensure_client()
        start = time.perf_counter()

        system_prompt = request.system_prompt or SYSTEM_PROMPT

        try:
            # Claude message format
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": request.prompt}
                ],
            })

            response = self._client.invoke_model(
                modelId=self._model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )

            response_body = json.loads(response["body"].read())
            content = response_body.get("content", [{}])[0].get("text", "")
            tokens = response_body.get("usage", {}).get("output_tokens", len(content.split()))

            latency = (time.perf_counter() - start) * 1000

            logger.info(
                "Bedrock generation: model=%s tokens=%d latency=%.1fms",
                self._model_id, tokens, latency,
            )

            return LLMResponse(
                content=content,
                model=self._model_id,
                provider=self.provider_name,
                tokens_used=tokens,
                latency_ms=round(latency, 2),
                metadata={
                    "stop_reason": response_body.get("stop_reason", ""),
                    "input_tokens": response_body.get("usage", {}).get("input_tokens", 0),
                },
            )

        except Exception as exc:
            logger.error("Bedrock generation failed: %s", exc, exc_info=True)
            raise RuntimeError(f"Bedrock generation failed: {exc}")

    async def generate_with_context(
        self,
        request: LLMRequest,
        context_documents: List[str],
    ) -> LLMResponse:
        """
        RAG-ready generation with context injection.
        Prepares for future LangChain retriever integration.
        """
        context_block = "\n\n---\n\n".join(context_documents)
        augmented_prompt = (
            f"CONTEXT (use this data to inform your analysis):\n\n"
            f"{context_block}\n\n"
            f"---\n\n"
            f"TASK:\n{request.prompt}"
        )

        augmented_request = LLMRequest(
            prompt=augmented_prompt,
            system_prompt=request.system_prompt or SYSTEM_PROMPT,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metadata={**request.metadata, "rag_enabled": True, "context_docs": len(context_documents)},
        )

        return await self.generate(augmented_request)

    async def health_check(self) -> Dict[str, Any]:
        """Check Bedrock connectivity."""
        try:
            self._ensure_client()
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "model": self._model_id,
                "region": settings.AWS_REGION,
                "initialized": self._initialized,
            }
        except Exception as exc:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(exc),
                "initialized": False,
            }
