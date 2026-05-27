"""
Configuración de tiers y modelos LLM.
Filosofía: No velocity, only precision 🐢💎
"""
from .types import TierConfig, LLMConfig

# Configuración completa de tiers de producción
LLM_TIERS: dict[str, TierConfig] = {
    "basico_97": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        story=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        reel=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        hashtags=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        bio=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        script=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        imagen=LLMConfig(
            primary="nano-banana",
            fallback=[],
            cache=False
        )
    ),

    "pro_197": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        story=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        reel=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        hashtags=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        ad=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        bio=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        script=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        carrusel=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        imagen=LLMConfig(
            primary="nano-banana",
            fallback=["nano-banana"],
            cache=False
        )
    ),

    "enterprise_497": TierConfig(
        post=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-opus-4-7", "anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        caption=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-opus-4-7", "anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        story=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        reel=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        hashtags=LLMConfig(
            primary="anthropic/claude-haiku-4-5-20251001",
            fallback=["anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        email=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-opus-4-7", "anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        anuncio=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-opus-4-7", "anthropic/claude-haiku-4-5-20251001"],
            cache=True
        ),
        bio=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        script=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        analytics=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-opus-4-7", "anthropic/claude-haiku-4-5-20251001"],
            cache=False
        ),
        carrusel=LLMConfig(
            primary="anthropic/claude-sonnet-4-6",
            fallback=["anthropic/claude-sonnet-4-6"],
            cache=True
        ),
        imagen=LLMConfig(
            primary="nano-banana",
            fallback=["nano-banana"],
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
