"""
Agent Dispatcher - Routes agent calls to correct AI provider.
DDD: Infrastructure layer - Orchestration logic.
Max 200L strict. Type-safe, no `any`.
"""
from typing import List, Optional, Dict, Any
import os
import logging
from .agent_registry import (
    get_agent_config,
    is_agent_registered,
    AgentConfig
)
from .providers import (
    BaseAIProvider,
    ChatMessage,
    AIProviderResponse,
    AnthropicProvider,
)
# Fase 2 §2.6: providers legacy no-Anthropic eliminados (DDD I1)

logger = logging.getLogger(__name__)


class AgentDispatcher:
    """
    Dispatches agent calls to correct AI provider.

    Principles:
    - Single Responsibility: Only routing/dispatching
    - Type Safety: No `any` types
    - Fallback: NOVA (CEO) if agent not found
    - Immutable: Stateless operations
    """

    def __init__(self) -> None:
        """Initialize dispatcher with API keys from environment.

        Fase 2 §2.6: solo Anthropic permitido. Otros providers eliminados (DDD I1).
        """
        self._api_keys: Dict[str, str] = {
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        }
        self._validate_api_keys()

    def _validate_api_keys(self) -> None:
        """Validate that all API keys are configured."""
        missing_keys = [
            provider for provider, key in self._api_keys.items()
            if not key or not key.strip()
        ]
        if missing_keys:
            logger.warning(
                f"Missing API keys for providers: {', '.join(missing_keys)}. "
                "These agents will fail if dispatched."
            )

    def _create_provider(
        self,
        provider_name: str,
        model_name: str
    ) -> BaseAIProvider:
        """
        Create provider instance based on name.

        Args:
            provider_name: Provider name (anthropic)
            model_name: Model identifier

        Returns:
            Initialized provider instance

        Raises:
            ValueError: If provider unknown or API key missing
        """
        api_key = self._api_keys.get(provider_name, "")
        if not api_key:
            raise ValueError(f"API key not configured for provider: {provider_name}")

        # Fase 2 §2.6: solo Anthropic permitido (DDD I1).
        # Otros providers eliminados; agent_registry mapea todos a "anthropic".
        if provider_name == "anthropic":
            return AnthropicProvider(api_key, model_name)
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            "Only 'anthropic' is permitted post-Fase 2 §2.6."
        )

    async def dispatch(
        self,
        agent_code: str,
        messages: List[ChatMessage],
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Dispatch agent call to appropriate provider.

        Args:
            agent_code: Agent code (e.g., "ATLAS", "RAFA")
            messages: Chat messages
            system_prompt: Optional system prompt
            max_tokens: Max tokens (default 4096)

        Returns:
            Dict with keys:
            - agent: str (agent code)
            - provider: str (provider name)
            - model: str (model name)
            - response: str (AI response content)
            - tokens_used: int (tokens consumed)
            - fallback_used: bool (whether fallback was triggered)

        Fallback:
            If agent not found, fallback to NOVA (Claude Sonnet 4.5)
        """
        fallback_used = False
        original_agent = agent_code
        config: AgentConfig

        # Get agent config (with fallback to NOVA)
        try:
            if not is_agent_registered(agent_code):
                logger.warning(
                    f"Agent '{agent_code}' not registered. "
                    "Falling back to NOVA (CEO)"
                )
                agent_code = "NOVA"
                fallback_used = True

            config = get_agent_config(agent_code)

        except KeyError as e:
            logger.error(f"Registry error: {e}. Falling back to NOVA")
            agent_code = "NOVA"
            config = get_agent_config("NOVA")
            fallback_used = True

        # Create provider and execute chat
        try:
            provider = self._create_provider(
                config["provider"],
                config["model"]
            )

            response: AIProviderResponse = await provider.chat(
                messages=messages,
                system_prompt=system_prompt,
                max_tokens=max_tokens
            )

            logger.info(
                f"Dispatched {original_agent} → {agent_code} "
                f"({config['provider']}/{config['model']}), "
                f"tokens={response.tokens_used}"
            )

            result: Dict[str, Any] = {
                "agent": agent_code,
                "provider": response.provider_name,
                "model": response.model_name,
                "response": response.content,
                "tokens_used": response.tokens_used,
                "fallback_used": fallback_used
            }

            if fallback_used:
                result["original_agent"] = original_agent

            return result

        except Exception as e:
            logger.error(
                f"Dispatch failed for {agent_code}: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise
