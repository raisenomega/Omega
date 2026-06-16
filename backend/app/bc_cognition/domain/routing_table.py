"""
OmegaRaisen — Tabla de routing Haiku/Sonnet/Opus por agente.

Cumple DDD I2: ningún agente decide su propio modelo. La tabla es la
fuente de verdad. Modificación requiere aprobación + test (X2).

Uso:
    from app.bc_cognition.domain.routing_table import resolve_model
    model_id = resolve_model("content_creator")  # → "claude-sonnet-4-6"
"""

from types import MappingProxyType
from typing import Final, Literal

ModelTier = Literal["haiku", "sonnet", "opus"]

# ─── Model IDs canónicos · fuente única de strings de modelo (P9 · verif. mayo 2026) ───
MODEL_HAIKU: Final[str] = "claude-haiku-4-5-20251001"
MODEL_SONNET: Final[str] = "claude-sonnet-4-6"
MODEL_OPUS: Final[str] = "claude-opus-4-7"
MODEL_IDS: Final[MappingProxyType] = MappingProxyType({
    "haiku": MODEL_HAIKU, "sonnet": MODEL_SONNET, "opus": MODEL_OPUS,
})

# ─── Asignación de tier por agente (≡ DDD_REGLAS_OMEGA.md tabla I2) ───
_AGENT_TIER_RAW: dict[str, ModelTier] = {
    # HAIKU — clasificación / lookup / texto corto
    "hashtag_generator":          "haiku",
    "emoji_suggestor":            "haiku",
    "caption_optimizer":          "haiku",
    "sentiment_analyzer":         "haiku",
    "bio_generator":              "haiku",
    "client_context_builder":     "haiku",
    "brand_voice_checker":        "haiku",
    "url_extractor":              "haiku",
    "pdf_extractor":              "haiku",

    # SONNET — workhorse / creatividad / decisiones tácticas
    "content_creator":            "sonnet",
    "strategy":                   "sonnet",
    "brand_voice":                "sonnet",
    "analytics":                  "sonnet",
    "scheduling":                 "sonnet",
    "copywriter":                 "sonnet",
    "trend_hunter":               "sonnet",
    "competitive_intelligence":   "sonnet",
    "monitor":                    "sonnet",
    "engagement":                 "sonnet",
    "seo_optimizer":              "sonnet",
    "image_prompt_writer":        "sonnet",
    "video_prompt_writer":        "sonnet",
    "community_moderator":        "sonnet",
    "influencer_scout":           "sonnet",
    "compliance_checker":         "sonnet",
    "quality_control":            "sonnet",
    "news_monitor":               "sonnet",
    "competitor_tracker":         "sonnet",
    "intelligence":               "sonnet",
    "guardian_consultor":         "sonnet",   # GUARDIAN consultor de seguridad (4B-5 · análisis incidents)

    # ARIA — proyección de NOVA · 4 niveles · spec ARIA_NOVA_INTELLIGENCE §6
    "aria_1":                     "haiku",
    "aria_2":                     "sonnet",
    "aria_3":                     "sonnet",
    "aria_4":                     "sonnet",   # Nivel 4 · Enterprise incluido o PRO+addons

    # OPUS — decisiones críticas / reputacionales / briefing ejecutivo
    "orchestrator":               "opus",
    "crisis_manager":             "opus",
    "oracle_service":             "opus",
    "nova_chat":                  "opus",
    "ab_testing_analysis":        "opus",
    "report_generator":           "opus",
    "audit_reviewer":             "opus",
    "growth_hacker":              "opus",
    "sentinel_security":          "opus",
}

AGENT_TIER: Final[MappingProxyType] = MappingProxyType(_AGENT_TIER_RAW)


def resolve_model(agent_code: str) -> str:
    """Retorna model_id Anthropic. KeyError si agente no registrado (cumple I2)."""
    return MODEL_IDS[AGENT_TIER[agent_code]]


def get_tier(agent_code: str) -> ModelTier:
    """Tier (haiku/sonnet/opus) del agente."""
    return AGENT_TIER[agent_code]


def is_registered(agent_code: str) -> bool:
    """¿El agente tiene routing asignado? (sin lanzar excepción)"""
    return agent_code in AGENT_TIER


# Self-check al importar
assert len(AGENT_TIER) >= 38, \
    f"❌ Routing table incompleta: {len(AGENT_TIER)} agentes (esperado ≥38)"
assert MODEL_SONNET == "claude-sonnet-4-6", "❌ Sonnet model_id incorrecto"
