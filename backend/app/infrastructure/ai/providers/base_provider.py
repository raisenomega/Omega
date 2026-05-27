"""
Base AI Provider Abstract Class
Defines the interface for all AI provider implementations.
DDD: Infrastructure layer - External AI service abstraction.
Max 200 lines strict.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    """Message role enum for type safety."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ChatMessage:
    """
    Immutable chat message structure.
    Type-safe, no `any` types allowed.
    """
    role: MessageRole
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dict for API calls."""
        return {
            "role": self.role.value,
            "content": self.content
        }


@dataclass(frozen=True)
class AIProviderResponse:
    """
    Immutable response from AI provider.
    Complete type safety for all fields.
    """
    content: str
    provider_name: str
    model_name: str
    tokens_used: int
    finish_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "content": self.content,
            "provider": self.provider_name,
            "model": self.model_name,
            "tokens_used": self.tokens_used,
            "finish_reason": self.finish_reason
        }


class BaseAIProvider(ABC):
    """
    Abstract base class for AI provider implementations.

    All providers must implement:
    - chat(): Main conversation method
    - get_provider_name(): Provider identification
    - get_model_name(): Model identification

    Principles:
    - Pure functions (no side effects in core logic)
    - Type safety (no `any`, no `unknown`)
    - Immutable responses (dataclasses with frozen=True)
    - Single responsibility (only AI communication)
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Initialize provider with API key and model.

        Args:
            api_key: API key for the provider
            model_name: Model identifier string

        Raises:
            ValueError: If api_key is empty or None
        """
        if not api_key or not api_key.strip():
            raise ValueError(f"API key required for {self.__class__.__name__}")

        self._api_key: str = api_key.strip()
        self._model_name: str = model_name

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> AIProviderResponse:
        """
        Execute chat completion with the AI model.

        Args:
            messages: List of chat messages (immutable)
            system_prompt: Optional system prompt for context
            max_tokens: Maximum tokens in response (default 4096)
            temperature: Randomness 0.0-1.0 (default 0.7)

        Returns:
            AIProviderResponse with complete type safety

        Raises:
            Exception: Provider-specific errors
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the provider name.

        Returns:
            Provider name string (e.g., "anthropic")
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the model name.

        Returns:
            Model identifier string (e.g., "claude-sonnet-4-6", "claude-opus-4-7")
        """
        pass

    def _validate_messages(self, messages: List[ChatMessage]) -> None:
        """
        Validate messages list.

        Args:
            messages: List of chat messages

        Raises:
            ValueError: If messages list is invalid
        """
        if not messages:
            raise ValueError("Messages list cannot be empty")

        if not all(isinstance(msg, ChatMessage) for msg in messages):
            raise ValueError("All messages must be ChatMessage instances")

    def _validate_temperature(self, temperature: float) -> None:
        """
        Validate temperature parameter.

        Args:
            temperature: Temperature value to validate

        Raises:
            ValueError: If temperature is out of range
        """
        if not 0.0 <= temperature <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {temperature}")

    def _validate_max_tokens(self, max_tokens: int) -> None:
        """
        Validate max_tokens parameter.

        Args:
            max_tokens: Max tokens value to validate

        Raises:
            ValueError: If max_tokens is invalid
        """
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")

        if max_tokens > 16384:
            raise ValueError(f"max_tokens exceeds limit of 16384, got {max_tokens}")
