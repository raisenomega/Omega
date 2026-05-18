"""
OpenAI Provider Implementation
GPT-4o and GPT-4o-mini support for OMEGA agents.
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


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI GPT-4o/GPT-4o-mini provider.

    Models:
    - gpt-4o: Full capability model for complex agents
    - gpt-4o-mini: Cost-efficient model for simple agents

    Used by: ATLAS, RAFA, DUDA, ECHO, LUAN, PIXEL (Marketing)
             REX, ANCHOR, BRIDGE, FLOW, SCOUT (Operations)
             SOPHIA, HIRE, TRAIN, CULTURE, COMPASS (People)
             SENTINEL + Security team (10 agents)
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o") -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model_name: Model name (gpt-4o or gpt-4o-mini)
        """
        super().__init__(api_key, model_name)
        self._client: AsyncOpenAI = AsyncOpenAI(api_key=self._api_key)
        self._validate_model(model_name)

    def _validate_model(self, model_name: str) -> None:
        """Validate OpenAI model name."""
        valid_models = ["gpt-4o", "gpt-4o-mini"]
        if model_name not in valid_models:
            raise ValueError(
                f"Invalid OpenAI model: {model_name}. "
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
        Execute OpenAI chat completion.

        Args:
            messages: Chat history
            system_prompt: Optional system prompt
            max_tokens: Max tokens (default 4096)
            temperature: Randomness 0.0-1.0

        Returns:
            AIProviderResponse with complete typing

        Raises:
            Exception: OpenAI API errors
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
                f"OpenAI {self._model_name}: {tokens_used} tokens, "
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
                f"OpenAI {self._model_name} error: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "openai"

    def get_model_name(self) -> str:
        """Get model name."""
        return self._model_name
