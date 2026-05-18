"""
Configuración de tiers y modelos LLM.
Filosofía: No velocity, only precision 🐢💎
"""
from .types import TierConfig, LLMConfig

# Configuración completa de tiers de producción
LLM_TIERS: dict[str, TierConfig] = {
    "basico_97": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-3.5-haiku",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o-mini"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-3.5-haiku",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o-mini"],
            cache=True
        ),
        story=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        reel=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        hashtags=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["groq/llama-3.3-70b"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-3.5-haiku",
            fallback=["deepseek/deepseek-chat"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-3.5-haiku",
            fallback=["deepseek/deepseek-chat"],
            cache=True
        ),
        bio=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        script=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        imagen=LLMConfig(
            primary="fal-ai/flux-schnell",
            fallback=[],
            cache=False
        )
    ),

    "pro_197": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        story=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku", "openai/gpt-4o-mini"],
            cache=False
        ),
        reel=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        hashtags=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["groq/llama-3.3-70b"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat"],
            cache=True
        ),
        ad=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat"],
            cache=True
        ),
        bio=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku"],
            cache=False
        ),
        script=LLMConfig(
            primary="deepseek/deepseek-chat",
            fallback=["anthropic/claude-3.5-haiku", "openai/gpt-4o-mini"],
            cache=False
        ),
        carrusel=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        imagen=LLMConfig(
            primary="fal-ai/flux-dev",
            fallback=["openai/dall-e-3"],
            cache=False
        )
    ),

    "enterprise_497": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/o1-mini", "deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/o1-mini", "deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        story=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        reel=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        hashtags=LLMConfig(
            primary="anthropic/claude-3.5-haiku",
            fallback=["deepseek/deepseek-chat"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/o1-mini", "deepseek/deepseek-chat"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/o1-mini", "deepseek/deepseek-chat"],
            cache=True
        ),
        bio=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        script=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["deepseek/deepseek-chat", "openai/gpt-4o"],
            cache=True
        ),
        analytics=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/o1-mini", "deepseek/deepseek-chat"],
            cache=False
        ),
        carrusel=LLMConfig(
            primary="anthropic/claude-sonnet-4",
            fallback=["openai/gpt-4o"],
            cache=True
        ),
        imagen=LLMConfig(
            primary="fal-ai/flux-pro-1.1",
            fallback=["openai/dall-e-3-hd"],
            cache=False
        )
    )
}

# Costos proyectados mensuales por tier
TIER_COSTS: dict[str, dict[str, int | float]] = {
    "basico_97": {"min": 5, "max": 10, "margin_pct": 90},
    "pro_197": {"min": 35, "max": 55, "margin_pct": 75},
    "enterprise_497": {"min": 150, "max": 220, "margin_pct": 65}
}
