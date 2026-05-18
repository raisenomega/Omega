"""
LLM Router - Wrapper class for multi-LLM routing
Filosofía: No velocity, only precision 🐢💎
"""
import logging
import json
from typing import Optional
from app.services.llm.router import generate_content

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Router class that wraps the generate_content function.
    Provides a simple interface for agent execution.
    """

    def __init__(self):
        """Initialize LLM Router"""
        pass

    async def route(
        self,
        prompt: str,
        tier: str = "premium",
        response_format: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Route LLM request to appropriate model based on tier.

        Args:
            prompt: User prompt
            tier: Tier level (basic, premium, enterprise)
            response_format: Format type (json_object, text)
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            str: Generated content
        """
        try:
            # Map tier to UserTier string literal
            tier_map = {
                "basic": "basico_97",
                "premium": "pro_197",
                "enterprise": "enterprise_497",
            }
            user_tier = tier_map.get(tier, "pro_197")

            # Default to generic content type (string literal)
            content_type = "caption"

            # Add response_format to kwargs if specified
            if response_format == "json_object":
                kwargs["response_format"] = {"type": "json_object"}

            # Call generate_content
            response = await generate_content(
                content_type=content_type,
                user_tier=user_tier,
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs
            )

            return response.content

        except Exception as e:
            logger.error(f"LLMRouter.route failed: {e}")
            raise
