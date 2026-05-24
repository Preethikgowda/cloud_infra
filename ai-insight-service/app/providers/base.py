"""
IntelliWealth – LLM Provider Interface
Abstract base class defining the contract for all LLM providers.

Supports future integration with:
- AWS Bedrock (Claude, Titan)
- LangChain agents
- RAG pipelines
- Custom fine-tuned models
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMRequest:
    """Structured request to an LLM provider."""
    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """
    Abstract LLM provider interface.

    All providers must implement:
    - generate(): Single completion
    - health_check(): Provider connectivity test

    Providers MAY implement:
    - generate_with_context(): RAG-ready completion with context docs
    """

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a completion from the LLM.

        Args:
            request: Structured LLM request with prompt and parameters.

        Returns:
            LLMResponse with generated content and metadata.
        """
        ...

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verify provider connectivity and readiness.

        Returns:
            Dict with status, provider name, and any diagnostics.
        """
        ...

    async def generate_with_context(
        self,
        request: LLMRequest,
        context_documents: List[str],
    ) -> LLMResponse:
        """
        RAG-ready generation with retrieval context.
        Default implementation prepends context to prompt.
        Override for provider-specific RAG implementations.
        """
        context_block = "\n\n---\n\n".join(context_documents)
        augmented_prompt = (
            f"Use the following context to inform your response:\n\n"
            f"{context_block}\n\n"
            f"---\n\n"
            f"{request.prompt}"
        )
        augmented_request = LLMRequest(
            prompt=augmented_prompt,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            metadata={**request.metadata, "rag_enabled": True},
        )
        return await self.generate(augmented_request)

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Model identifier."""
        ...
