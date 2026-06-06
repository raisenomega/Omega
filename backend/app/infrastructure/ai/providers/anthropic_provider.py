"""
Anthropic Provider Implementation
Claude Sonnet 4.5 support for NOVA (CEO Agent).
DDD: Infrastructure layer. Max 200L strict.
"""
from typing import List, Optional
import logging
from anthropic import AsyncAnthropic
from .base_provider import (
    BaseAIProvider,
    AIProviderResponse,
    ChatMessage,
    MessageRole
)

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude V3 provider (Haiku/Sonnet/Opus 4.5-4.7).

    Default model: claude-sonnet-4-6 (post §2.6 bump · DEBT-023 cerrada)
    Used by: agent_dispatcher for all 45 OMEGA agents (Anthropic-only post §2.6).

    Note: Does NOT replace claude_service.py (legacy compatibility · DEBT-024).
    """

    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4-6") -> None:
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model_name: Model name (default claude-sonnet-4-6)
        """
        super().__init__(api_key, model_name)
        self._client: AsyncAnthropic = AsyncAnthropic(api_key=self._api_key)
        self._validate_model(model_name)

    def _validate_model(self, model_name: str) -> None:
        """Validate Claude V3 model name (Haiku/Sonnet/Opus)."""
        valid_models = [
            "claude-haiku-4-5-20251001",   # V3 Haiku · workhorse económico
            "claude-sonnet-4-6",            # V3 Sonnet · default
            "claude-opus-4-7",              # V3 Opus · razonamiento crítico
        ]
        if model_name not in valid_models:
            raise ValueError(
                f"Invalid Claude model: {model_name}. "
                f"Valid models: {', '.join(valid_models)}"
            )

    async def chat(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.7
    ) -> AIProviderResponse:
        """
        Execute Claude chat completion.

        Args:
            messages: Chat history
            system_prompt: Optional system prompt
            max_tokens: Max tokens (default 8192 for NOVA)
            temperature: Randomness 0.0-1.0

        Returns:
            AIProviderResponse with complete typing

        Raises:
            Exception: Anthropic API errors
        """
        self._validate_messages(messages)
        self._validate_temperature(temperature)
        # Claude supports up to 200K tokens but we limit to 16K
        if max_tokens > 16384:
            max_tokens = 16384

        # Claude requires alternating user/assistant messages
        api_messages: List[dict] = []
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                api_messages.append(msg.to_dict())

        try:
            response = await self._client.messages.create(
                model=self._model_name,
                max_tokens=max_tokens,
                system=system_prompt or "",
                messages=api_messages  # type: ignore
            )

            content: str = response.content[0].text
            tokens_used: int = response.usage.input_tokens + response.usage.output_tokens
            finish_reason: Optional[str] = response.stop_reason

            logger.info(
                f"Claude {self._model_name}: {tokens_used} tokens, "
                f"finish={finish_reason}"
            )

            return AIProviderResponse(
                content=content,
                provider_name=self.get_provider_name(),
                model_name=self.get_model_name(),
                tokens_used=tokens_used,
                finish_reason=finish_reason
            )

        except Exception as e:
            logger.error(
                f"Claude {self._model_name} error: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "anthropic"

    def get_model_name(self) -> str:
        """Get model name."""
        return self._model_name
