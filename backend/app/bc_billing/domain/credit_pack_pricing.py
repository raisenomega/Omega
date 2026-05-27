"""Credit Pack → Stripe Price ID lookup. Capa pura · DDD (DEBT-052 FASE 4).

4 credit packs (budget mensual prepagado de API · texto/imagen): micro $9 /
starter $25 / plus $59 / ultra $119. SEPARADOS del plan base ($29/$65/$199) y de
los video packs (§4.4). Convención idéntica a plan_pricing: lee de settings (no
os.getenv directo · DEBT-029); price vacío/whitespace → None → handler 503.
Los budgets USD viven en domain/credit_costs.PACK_BUDGETS_USD (no duplicar acá).
"""
from typing import Literal, Optional, FrozenSet
from app.config import settings

CreditPackCode = Literal["micro", "starter", "plus", "ultra"]

CREDIT_PACK_CODES: FrozenSet[str] = frozenset({"micro", "starter", "plus", "ultra"})


def get_price_id_for_credit_pack(credit_pack_code: str) -> Optional[str]:
    """Resuelve Stripe Price ID del credit pack. None si vacío/whitespace (→503)."""
    price_map = {
        "micro": settings.stripe_price_credit_pack_micro,
        "starter": settings.stripe_price_credit_pack_starter,
        "plus": settings.stripe_price_credit_pack_plus,
        "ultra": settings.stripe_price_credit_pack_ultra,
    }
    raw = price_map.get(credit_pack_code, "") or ""
    cleaned = raw.strip()
    return cleaned or None
