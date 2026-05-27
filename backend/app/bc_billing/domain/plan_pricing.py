"""Plan + Addon → Stripe Price ID lookup. Capa pura · DDD.

Convención: lee de `app.config.settings` (no `os.getenv` directo · evita
DEBT-029). Si Price ID está vacío/whitespace en .env → retorna None y el
handler responde 503 'plan no configurado'.

Modelo C canónico (firmado 17 may 2026 · MODELO_NEGOCIO_OMEGA_CLIENTE §3):
- adopcion : $0 · 7 días gratis · NO requiere checkout (trigger auto-provision)
- basic    : $29/mes  ·  pro: $65/mes  ·  enterprise: stripe_price_enterprise
Addons/video packs: ver get_price_id_for_addon / get_price_id_for_video_pack.
"""
from typing import Literal, Optional, FrozenSet, Tuple
from app.config import settings

PlanCode = Literal["adopcion", "basic", "pro", "enterprise"]
AddonCode = Literal["aria_premium_client", "aria_premium_reseller"]
VideoPackCode = Literal["starter", "creator", "cinematic_pro"]

ADDON_CODES: FrozenSet[str] = frozenset({"aria_premium_client", "aria_premium_reseller"})
VIDEO_PACK_CODES: FrozenSet[str] = frozenset({"starter", "creator", "cinematic_pro"})

# Caminos de upgrade (checkout inmediato). Enterprise self-serve (DEBT-076).
UPGRADE_PATHS: FrozenSet[Tuple[str, str]] = frozenset({
    ("adopcion", "basic"), ("adopcion", "pro"), ("adopcion", "enterprise"),
    ("basic", "pro"), ("basic", "enterprise"), ("pro", "enterprise"),
})

# Downgrades (DEBT-076): se PROGRAMAN a fin de ciclo vía Stripe SubscriptionSchedule.
DOWNGRADE_PATHS: FrozenSet[Tuple[str, str]] = frozenset({
    ("pro", "basic"), ("enterprise", "pro"), ("enterprise", "basic"),
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


def is_valid_downgrade(current_plan: str, target_plan: str) -> bool:
    """DEBT-076 · valida downgrade (se programa a fin de ciclo, no inmediato)."""
    return (current_plan, target_plan) in DOWNGRADE_PATHS


def plan_for_price_id(price_id: str) -> Optional[str]:
    """DEBT-076 · reverse map Stripe price → plan (webhook sync al aplicar downgrade)."""
    pid = (price_id or "").strip()
    if not pid:
        return None
    for plan, raw in (
        ("basic", settings.stripe_price_basic),
        ("pro", settings.stripe_price_pro),
        ("enterprise", settings.stripe_price_enterprise),
    ):
        if (raw or "").strip() == pid:
            return plan
    return None


def get_price_id_for_addon(addon_code: str) -> Optional[str]:
    """Resuelve Stripe Price ID para addon. DEBT-037 V1 · DEBT-046 reseller futuro."""
    price_map = {
        "aria_premium_client": settings.stripe_price_aria_premium_client,
        "aria_premium_reseller": settings.stripe_price_aria_premium_reseller,
    }
    raw = price_map.get(addon_code, "") or ""
    cleaned = raw.strip()
    return cleaned or None


def get_price_id_for_video_pack(video_pack_code: str) -> Optional[str]:
    """Resuelve Stripe Price ID para video pack. DEBT-VID-001.
    Returns None si Price ID vacío/whitespace (TODO Stripe Dashboard)."""
    price_map = {
        "starter": settings.stripe_price_video_pack_starter,
        "creator": settings.stripe_price_video_pack_creator,
        "cinematic_pro": settings.stripe_price_video_pack_cinematic_pro,
    }
    raw = price_map.get(video_pack_code, "") or ""
    cleaned = raw.strip()
    return cleaned or None
