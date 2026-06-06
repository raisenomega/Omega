"""OmegaRaisen — Identidad canónica de agentes (fuente única · ROLES_CANONICO §2-§3).

8 operativos + SOPHIA (latente) + GUARDIAN (sub-sistema). Los nombres legacy son
ALIAS que resuelven a un code de dispatch real (routing_table I2) o a None=INACTIVE
(OMEGA Company futuro · respuesta honesta, NO fallback silencioso).
Dominio puro (A2): sin imports externos. Modelos alineados a routing_table.
"""
from typing import Final, Optional
from types import MappingProxyType

CANONICAL_AGENTS: Final[MappingProxyType] = MappingProxyType({
    "nova_chat":         {"name": "NOVA",            "model": "claude-opus-4-7",   "role": "Cerebro central · orquesta · solo Ibrain", "status": "operational"},
    "orchestrator":      {"name": "ORCHESTRATOR",    "model": "claude-opus-4-7",   "role": "Ejecuta chains multi-agente", "status": "operational"},
    "content_creator":   {"name": "CONTENT CREATOR", "model": "claude-sonnet-4-6", "role": "Motor de contenido (texto/imagen/video)", "status": "operational"},
    "strategy":          {"name": "STRATEGY",        "model": "claude-sonnet-4-6", "role": "Plan, timing, tendencias, competidores", "status": "operational"},
    "brand_voice":       {"name": "BRAND VOICE",     "model": "claude-sonnet-4-6", "role": "Valida consistencia de marca (7 gates)", "status": "operational"},
    "analytics":         {"name": "ANALYTICS",       "model": "claude-sonnet-4-6", "role": "Datos, insights, cierra loop was_correct", "status": "operational"},
    "crisis_manager":    {"name": "CRISIS MANAGER",  "model": "claude-opus-4-7",   "role": "Clasifica crisis · draft · NUNCA publica", "status": "operational"},
    "sentinel_security": {"name": "SENTINEL",        "model": "claude-opus-4-7",   "role": "Seguridad infra · bloquea deploy <95", "status": "operational"},
    "sophia":            {"name": "SOPHIA",          "model": "claude-opus-4-7",   "role": "Meta-agente · crea agentes con evidencia", "status": "latent"},
    "guardian":          {"name": "GUARDIAN",        "model": "claude-sonnet-4-6", "role": "Seguridad de comportamiento (humanos)", "status": "subsystem"},
})

# Community-facing → engagement (code operativo real · clase engagement_agent.py · routing_table sonnet).
# ARIA = cara cliente; NOVA NO delega a su propia cara. Quejas graves escalan a crisis_manager
# dentro de la lógica del agente, no como alias default.
_ENGAGEMENT = "engagement"

LEGACY_ALIASES: Final[MappingProxyType] = MappingProxyType({
    "NOVA": "nova_chat",
    "ATLAS": "strategy", "DUDA": "strategy", "TREND": "strategy", "SCOUT": "strategy", "LUAN": "strategy",
    "RAFA": "content_creator", "PIXEL": "content_creator",
    "ORACLE": "analytics", "LENS": "analytics", "MAP": "analytics", "SIGNAL": "analytics",
    "ECHO": _ENGAGEMENT, "ANCHOR": _ENGAGEMENT, "BRIDGE": _ENGAGEMENT, "KIRA": _ENGAGEMENT,
    "REVIEW": _ENGAGEMENT, "NURTURE": _ENGAGEMENT, "TRIBE": _ENGAGEMENT, "VOICE": _ENGAGEMENT,
    "SENTINEL": "sentinel_security", "VAULT": "sentinel_security", "PULSE_MON": "sentinel_security",
    "WATCH": "sentinel_security", "LOCK": "sentinel_security", "TRACE": "sentinel_security",
    "AUDIT": "sentinel_security", "SHIELD_SEC": "sentinel_security", "CIPHER": "sentinel_security",
    "PERIMETER": "sentinel_security", "RESPONSE": "sentinel_security", "SCAN": "sentinel_security",
    "GUARD": "guardian",
    "SOPHIA": "sophia",
    # INACTIVE · OMEGA Company futuro (no operativos hoy)
    "LUNA": None, "SHIELD": None, "FORGE": None, "DEBUG": None, "SCOPE": None,
    "REX": None, "FLOW": None,
    "VERA": None, "LEDGER": None, "PULSE_FIN": None, "QUOTA": None, "MARGIN": None,
    "HIRE": None, "TRAIN": None, "CULTURE": None, "COMPASS": None,
})


def resolve_alias(name: str) -> Optional[str]:
    """Nombre legacy o code → code de dispatch. None si INACTIVE o desconocido."""
    key = name.upper().strip().lstrip("@")
    if key in LEGACY_ALIASES:
        return LEGACY_ALIASES[key]
    return key.lower() if key.lower() in CANONICAL_AGENTS else None


def is_inactive_alias(name: str) -> bool:
    """True si el nombre existe pero es INACTIVE (OMEGA Company futuro)."""
    key = name.upper().strip().lstrip("@")
    return key in LEGACY_ALIASES and LEGACY_ALIASES[key] is None


def operational_count() -> int:
    return sum(1 for a in CANONICAL_AGENTS.values() if a["status"] == "operational")


# Self-check al importar (espejo de routing_table)
assert operational_count() == 8, f"Operativos != 8: {operational_count()}"
assert CANONICAL_AGENTS["sophia"]["status"] == "latent"
assert CANONICAL_AGENTS["guardian"]["status"] == "subsystem"
