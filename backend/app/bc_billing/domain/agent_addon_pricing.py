"""Agent Add-On → Stripe Price ID lookup. Capa pura · DDD (DEBT-091).

5 agent add-ons (recurring monthly · /add-ons "Agentes IA"): Publicador (Rex)
esencial $19 / pro $29 · Creativo (Rafa) esencial $25 / pro $35 · Tendencias
(Maya) único $15. Códigos alineados con src/components/addons/_*_packs_data.ts.
Convención idéntica a credit_pack_pricing: lee de settings · vacío → None → 503.
"""
from typing import Literal, Optional, FrozenSet
from app.config import settings

AgentAddonCode = Literal[
    "publisher_esencial", "publisher_pro",
    "creative_esencial", "creative_pro", "trends_unico",
]

AGENT_ADDON_CODES: FrozenSet[str] = frozenset({
    "publisher_esencial", "publisher_pro",
    "creative_esencial", "creative_pro", "trends_unico",
})


def get_price_id_for_agent_addon(agent_addon_code: str) -> Optional[str]:
    """Resuelve Stripe Price ID del agent add-on. None si vacío/whitespace (→503)."""
    price_map = {
        "publisher_esencial": settings.stripe_price_agent_publisher_esencial,
        "publisher_pro": settings.stripe_price_agent_publisher_pro,
        "creative_esencial": settings.stripe_price_agent_creative_esencial,
        "creative_pro": settings.stripe_price_agent_creative_pro,
        "trends_unico": settings.stripe_price_agent_trends_unico,
    }
    raw = price_map.get(agent_addon_code, "") or ""
    cleaned = raw.strip()
    return cleaned or None
