"""
Multi-AI Provider System — Anthropic-only post Fase 2 §2.6 (DDD I1)
Filosofía: No velocity, only precision 🐢💎
"""
import logging
import os
from typing import Optional, Dict, Any
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class AIProviders:
    """Anthropic-only provider system post Fase 2 §2.6.

    §2.6: todos los directors usan Anthropic (DDD I1 · proveedores legacy
    eliminados). Ver `agent_registry.py` para el mapping de 45 agents a
    modelos Anthropic V3 (Haiku/Sonnet/Opus). Unificar eventualmente con
    `bc_cognition.infrastructure.anthropic_adapter` V3 (DEBT-025).
    """

    DIRECTORS = {
        "NOVA": {
            "provider": "anthropic",
            "model": "claude-sonnet-4-6",
            "description": "Claude Sonnet 4.6 — OMEGA Chief Director",
            "strengths": ["Long-form", "Analysis", "Strategy"],
            "default": True,
        },
    }

    def __init__(self):
        """Initialize Anthropic client (only provider permitido post §2.6 · I1)."""
        self.anthropic = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def get_default_director(self) -> str:
        return "NOVA"

    def list_directors(self) -> Dict[str, Dict[str, Any]]:
        return self.DIRECTORS

    async def generate(
        self,
        director: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate content using specified director's Anthropic model."""
        config = self.DIRECTORS.get(director)
        if not config:
            logger.warning(f"Unknown director '{director}', falling back to NOVA")
            config = self.DIRECTORS["NOVA"]
        model = config["model"]
        logger.info(f"Generating with {director} (anthropic/{model})")
        try:
            response = await self.anthropic.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )
            return {
                "content": response.content[0].text,
                "provider": "anthropic",
                "model": model,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
            }
        except Exception as e:
            logger.error(
                f"Generation failed for {director}: {type(e).__name__}: {e}",
                exc_info=True,
            )
            raise
