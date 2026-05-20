"""Plan → Stripe Price ID lookup. Capa pura · DDD.

Convención: lee de `app.config.settings` (no `os.getenv` directo · evita
DEBT-029). Si Price ID está vacío/whitespace en .env → retorna None y el
handler responde 503 'plan no configurado'.

Modelo C canónico (firmado 17 may 2026 · MODELO_NEGOCIO_OMEGA_CLIENTE §3):
- adopcion : $0 · 7 días gratis · NO requiere checkout (trigger auto-provision)
- basic    : $29/mes
- pro      : $65/mes
- enterprise: personalizado · sin Price ID hasta Fase 3
"""
from typing import Literal, Optional, FrozenSet, Tuple
from app.config import settings

PlanCode = Literal["adopcion", "basic", "pro", "enterprise"]

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
