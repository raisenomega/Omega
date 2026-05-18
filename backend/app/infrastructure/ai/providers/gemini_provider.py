"""
Google Gemini Provider Implementation
Gemini 2.0 Flash support for OMEGA agents.
DDD: Infrastructure layer. Max 200L strict.
"""
from typing import List, Optional
import logging
import httpx
from .base_provider import (
    BaseAIProvider,
    AIProviderResponse,
    ChatMessage
)

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini 2.0 Flash provider.

    Model: gemini-2.0-flash-exp
    Used by: VERA, LEDGER, PULSE_FIN, QUOTA, MARGIN (Finance team)
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp") -> None:
        """
        Initialize Gemini provider.

        Args:
            api_key: Gemini API key
            model_name: Model name (gemini-2.0-flash-exp)
        """
        super().__init__(api_key, model_name)
        self._base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self._validate_model(model_name)

    def _validate_model(self, model_name: str) -> None:
        """Validate Gemini model name."""
        valid_models = ["gemini-2.0-flash-exp", "gemini-2.0-flash"]
        if model_name not in valid_models:
            raise ValueError(
                f"Invalid Gemini model: {model_name}. "
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
        Execute Gemini chat completion.

        Args:
            messages: Chat history
            system_prompt: Optional system prompt
            max_tokens: Max tokens (default 4096)
            temperature: Randomness 0.0-1.0

        Returns:
            AIProviderResponse with complete typing

        Raises:
            Exception: Gemini API errors
        """
        self._validate_messages(messages)
        self._validate_temperature(temperature)
        self._validate_max_tokens(max_tokens)

        # Build prompt (Gemini uses single prompt, not messages array)
        full_prompt = ""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n"

        for msg in messages:
            full_prompt += f"{msg.role.value.upper()}: {msg.content}\n"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                url = f"{self._base_url}/{self._model_name}:generateContent"
                response = await client.post(
                    url,
                    params={"key": self._api_key},
                    json={
                        "contents": [{"parts": [{"text": full_prompt}]}],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()

            content: str = data["candidates"][0]["content"]["parts"][0]["text"]
            tokens_used: int = data.get("usageMetadata", {}).get("totalTokenCount", 0)

            logger.info(f"Gemini {self._model_name}: {tokens_used} tokens")

            return AIProviderResponse(
                content=content,
                provider_name=self.get_provider_name(),
                model_name=self.get_model_name(),
                tokens_used=tokens_used,
                finish_reason="stop"
            )

        except Exception as e:
            logger.error(
                f"Gemini {self._model_name} error: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "gemini"

    def get_model_name(self) -> str:
        """Get model name."""
        return self._model_name
