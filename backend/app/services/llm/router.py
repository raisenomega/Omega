"""
Router multi-LLM con fallback automático.
Fase 2 §2.6: Anthropic-only post hot-swap (DDD I1).
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging

from app.infrastructure.ai.claude_service import claude_service
from app.domain.llm.types import (
    ContentType, UserTier, LLMResponse
)
from app.domain.llm.config import LLM_TIERS

logger = logging.getLogger(__name__)


async def generate_content(
    content_type: ContentType,
    user_tier: UserTier,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs,
) -> LLMResponse:
    """Generate content via Anthropic (post Fase 2 §2.6 swap from multi-LLM).

    Tier config preserved para futuro cost-based routing entre modelos
    Anthropic (Haiku/Sonnet/Opus). Actualmente todos los tiers usan
    `claude_service` que hardcodea Sonnet 4.5 — bump a V3 pending (DEBT-023).
    """
    CONTENT_TYPE_MAP = {"image": "imagen", "ad": "anuncio"}
    normalized_type = CONTENT_TYPE_MAP.get(content_type, content_type)

    if user_tier not in LLM_TIERS:
        base_tier = user_tier.split('_')[0] if '_' in user_tier else user_tier
        fallback_map = {
            "basico": "basico_97",
            "pro": "pro_197",
            "enterprise": "enterprise_497",
        }
        user_tier = fallback_map.get(base_tier, "pro_197")
        logger.warning(f"Tier not found, using fallback: {user_tier}")

    tier_config = LLM_TIERS[user_tier]
    content_config = getattr(tier_config, normalized_type, None)
    if not content_config:
        raise ValueError(
            f"Content type '{content_type}' no configurado para tier '{user_tier}'"
        )

    try:
        text = await claude_service.generate_text(
            prompt=prompt,
            system_message=system_prompt,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000),
        )

        logger.info(
            f"Generated {content_type} for {user_tier} via anthropic/claude-sonnet "
            f"(legacy claude_service · DEBT-023/024)"
        )

        return LLMResponse(
            content=text,
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            cached=False,
            tokens_used=0,
            cost_usd=None,
        )

    except Exception as e:
        logger.error(f"LLM generation failed for {user_tier}/{content_type}: {e}")
        raise


async def generate_image(
    user_tier: UserTier,
    prompt: str,
    style: str = "realistic",
    **kwargs,
) -> LLMResponse:
    """Image generation stub.

    Fase 2 §2.4: image generation moved to
    `bc_cognition.infrastructure._image_compat.generate_image_compat`.
    This stub stays for API compatibility but raises NotImplementedError.
    Callers should use the compat layer directly.
    """
    logger.info(
        f"Image generation requested for {user_tier} with style {style} — "
        "use _image_compat.generate_image_compat in bc_cognition instead"
    )
    raise NotImplementedError(
        "llm/router.generate_image is deprecated · use "
        "bc_cognition.infrastructure._image_compat.generate_image_compat"
    )
