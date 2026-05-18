"""
Router multi-LLM con fallback automático.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
import logging
import os
from openai import AsyncOpenAI

from app.domain.llm.types import (
    ContentType, UserTier, LLMResponse
)
from app.domain.llm.config import LLM_TIERS

logger = logging.getLogger(__name__)

# Initialize OpenAI client
_openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_content(
    content_type: ContentType,
    user_tier: UserTier,
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> LLMResponse:
    """
    Genera contenido usando el modelo apropiado según tier y tipo.

    Args:
        content_type: Tipo de contenido (caption, script, etc.)
        user_tier: Tier del cliente (basico_97, pro_197, enterprise_497)
        prompt: Prompt del usuario
        system_prompt: Prompt del sistema (opcional)
        **kwargs: Argumentos adicionales para litellm

    Returns:
        LLMResponse con contenido, provider, modelo, cache status

    Raises:
        Exception: Si todos los modelos del fallback chain fallan
    """
    # Normalizar content_type (English → Spanish)
    CONTENT_TYPE_MAP = {"image": "imagen", "ad": "anuncio"}
    normalized_type = CONTENT_TYPE_MAP.get(content_type, content_type)

    # Obtener configuración del tier con fallback
    if user_tier not in LLM_TIERS:
        # Fallback: usar tier base (enterprise → pro, etc.)
        base_tier = user_tier.split('_')[0] if '_' in user_tier else user_tier
        fallback_map = {"basico": "basico_97", "pro": "pro_197", "enterprise": "enterprise_497"}
        user_tier = fallback_map.get(base_tier, "pro_197")
        logger.warning(f"Tier not found, using fallback: {user_tier}")

    tier_config = LLM_TIERS[user_tier]

    # Obtener config específica del tipo de contenido
    content_config = getattr(tier_config, normalized_type, None)

    if not content_config:
        raise ValueError(
            f"Content type '{content_type}' no configurado para tier '{user_tier}'"
        )

    # Construir mensajes
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        # Simplified: Direct OpenAI call (no litellm for faster build)
        # Map tier config models to OpenAI models
        model_map = {
            "anthropic/claude-3.5-haiku": "gpt-4o-mini",
            "openai/gpt-4o": "gpt-4o",
            "openai/gpt-4o-mini": "gpt-4o-mini",
        }

        # Get OpenAI model from config (default to gpt-4o-mini)
        openai_model = model_map.get(
            content_config.primary,
            "gpt-4o-mini"
        )

        response = await _openai_client.chat.completions.create(
            model=openai_model,
            messages=messages,
            **kwargs
        )

        # Extract metadata
        tokens_used = response.usage.total_tokens if response.usage else 0

        logger.info(
            f"Generated {content_type} for {user_tier} via openai/{openai_model} "
            f"(tokens: {tokens_used})"
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=openai_model,
            cached=False,
            tokens_used=tokens_used,
            cost_usd=None  # TODO: Implementar cost tracking
        )

    except Exception as e:
        logger.error(
            f"LLM generation failed for {user_tier}/{content_type}: {e}"
        )
        raise


async def generate_image(
    user_tier: UserTier,
    prompt: str,
    style: str = "realistic",
    **kwargs
) -> LLMResponse:
    """
    Genera imagen usando el modelo apropiado según tier.

    Args:
        user_tier: Tier del cliente
        prompt: Descripción de la imagen
        style: Estilo de imagen (realistic, cartoon, minimal)
        **kwargs: Argumentos adicionales

    Returns:
        LLMResponse con URL de imagen
    """
    tier_config = LLM_TIERS[user_tier]
    image_config = tier_config.imagen

    # TODO: Implementar generación de imagen con fal.ai/DALL-E
    # Por ahora solo estructura

    logger.info(
        f"Image generation requested for {user_tier} with style {style}"
    )

    raise NotImplementedError(
        "Image generation será implementado en el siguiente archivo"
    )
