"""Plan + Addon → Stripe Price ID lookup. Capa pura · DDD.

Convención: lee de `app.config.settings` (no `os.getenv` directo · evita
DEBT-029). Si Price ID está vacío/whitespace en .env → retorna None y el
handler responde 503 'plan no configurado'.

Modelo C canónico (firmado 17 may 2026 · MODELO_NEGOCIO_OMEGA_CLIENTE §3):
- adopcion : $0 · 7 días gratis · NO requiere checkout (trigger auto-provision)
- basic    : $29/mes  ·  pro: $65/mes  ·  enterprise: personalizado

Addons (DEBT-037 V1 · DEBT-046 reseller futuro):
- aria_premium_client : $12/mes · sube clients.aria_level +1 (max 4)
- aria_premium_reseller: $25/mes · DEBT-046 futuro
"""
from typing import Literal, Optional, FrozenSet, Tuple
from app.config import settings

PlanCode = Literal["adopcion", "basic", "pro", "enterprise"]
AddonCode = Literal["aria_premium_client", "aria_premium_reseller"]

ADDON_CODES: FrozenSet[str] = frozenset({"aria_premium_client", "aria_premium_reseller"})

# Caminos válidos de upgrade per spec §2 camino natural del cliente:
# Adopción → Básico → Pro. Downgrades (pro→basic) bloqueados desde UI.
UPGRADE_PATHS: FrozenSet[Tuple[str, str]] = frozenset({
    ("adopcion", "basic"),
    ("adopcion", "pro"),
    ("basic", "pro"),
})


def get_price_id_for_plan(plan: str) -> Optional[str]:
    """Resuelve Stripe Price ID para el plan especificado.

    Returns None si:
    - plan == 'adopcion' (trial gratis · trigger auto-provision lo cubre)
    - Price ID en settings está vacío/whitespace (TODO Stripe Dashboard)
    """
    if plan == "adopcion":
        return None

    price_map = {
        "basic": settings.stripe_price_basic,
        "pro": settings.stripe_price_pro,
        "enterprise": settings.stripe_price_enterprise,
    }
    raw = price_map.get(plan, "") or ""
    cleaned = raw.strip()
    return cleaned or None


def is_valid_upgrade(current_plan: str, target_plan: str) -> bool:
    """Valida que el upgrade tenga sentido per spec §2."""
    return (current_plan, target_plan) in UPGRADE_PATHS


def get_price_id_for_addon(addon_code: str) -> Optional[str]:
    """Resuelve Stripe Price ID para addon. DEBT-037 V1 · DEBT-046 reseller futuro."""
    price_map = {
        "aria_premium_client": settings.stripe_price_aria_premium_client,
        "aria_premium_reseller": settings.stripe_price_aria_premium_reseller,
    }
    raw = price_map.get(addon_code, "") or ""
    cleaned = raw.strip()
    return cleaned or None
