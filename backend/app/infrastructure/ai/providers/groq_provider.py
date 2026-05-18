"""
Groq Provider Implementation
Llama 3.3 70B via Groq for ultra-fast inference.
DDD: Infrastructure layer. Max 200L strict.
"""
from typing import List, Optional
import logging
from openai import AsyncOpenAI
from .base_provider import (
    BaseAIProvider,
    AIProviderResponse,
    ChatMessage,
    MessageRole
)

logger = logging.getLogger(__name__)


class GroqProvider(BaseAIProvider):
    """
    Groq Llama 3.3 70B provider.

    Model: llama-3.3-70b-versatile (ultra-fast inference)
    Used by: KIRA, REVIEW, NURTURE, TRIBE, VOICE (Community team)
    """

    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile") -> None:
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key
            model_name: Model name (llama-3.3-70b-versatile)
        """
        super().__init__(api_key, model_name)
        self._client: AsyncOpenAI = AsyncOpenAI(
            api_key=self._api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self._validate_model(model_name)

    def _validate_model(self, model_name: str) -> None:
        """Validate Groq model name."""
        valid_models = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"]
        if model_name not in valid_models:
            raise ValueError(
                f"Invalid Groq model: {model_name}. "
                f"Valid models: {', '.join(valid_models)}"
            )

    async def chat(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> AIProviderResponse:
        """
        Execute Groq chat completion.

        Args:
            messages: Chat history
            system_prompt: Optional system prompt
            max_tokens: Max tokens (default 4096)
            temperature: Randomness 0.0-1.0

        Returns:
            AIProviderResponse with complete typing

        Raises:
            Exception: Groq API errors
        """
        self._validate_messages(messages)
        self._validate_temperature(temperature)
        self._validate_max_tokens(max_tokens)

        # Build messages array
        api_messages: List[dict] = []

        if system_prompt:
            api_messages.append({
                "role": MessageRole.SYSTEM.value,
                "content": system_prompt
            })

        api_messages.extend([msg.to_dict() for msg in messages])

        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=api_messages,  # type: ignore
                max_tokens=max_tokens,
                temperature=temperature
            )

            content: str = response.choices[0].message.content or ""
            tokens_used: int = response.usage.total_tokens if response.usage else 0
            finish_reason: Optional[str] = response.choices[0].finish_reason

            logger.info(
                f"Groq {self._model_name}: {tokens_used} tokens, "
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
                f"Groq {self._model_name} error: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "groq"

    def get_model_name(self) -> str:
        """Get model name."""
        return self._model_name
