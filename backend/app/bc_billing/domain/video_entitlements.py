"""OmegaRaisen — Video entitlements por plan y add-on packs.

Capa pura · cero imports externos (DDD A2). Define cuotas y duraciones
de video según MODELO_NEGOCIO_OMEGA_CLIENTE.md §3 + §4.4 (aprobado 23 may 2026).

Estos NO son safety limits (esos viven en limits_omega.py). Son entitlements
de billing — qué incluye cada plan/add-on en términos de generación Veo 3.1.

Uso:
    from app.bc_billing.domain.video_entitlements import (
        VIDEO_PLAN_INCLUDED, VIDEO_PACK_ENTITLEMENTS, get_pack
    )
    pack = get_pack("starter")            # → {"videos_per_month": 6, ...}
    base = VIDEO_PLAN_INCLUDED["pro"]     # → {"videos": 2, "seconds": 8, ...}
"""

from types import MappingProxyType
from typing import Final, FrozenSet

# Base incluida en el plan (sin add-on)
_PLAN_BASE = {
    "adopcion": {"videos": 0, "seconds": 0, "scope": "none"},
    "basic":    {"videos": 1, "seconds": 8, "scope": "lifetime"},  # cebo · 1 sola vez
    "pro":      {"videos": 2, "seconds": 8, "scope": "monthly"},
}
VIDEO_PLAN_INCLUDED: Final[MappingProxyType] = MappingProxyType({
    k: MappingProxyType(v) for k, v in _PLAN_BASE.items()
})

# Video Packs recurrentes mensuales (§4.4 MODELO_NEGOCIO)
_PACK_DATA = {
    "starter": {
        "price_usd": 39, "videos_per_month": 6, "seconds_per_video": 8,
        "includes_aria_script": False, "includes_brand_voice_review": False,
        "includes_dedicated_agent": False,
    },
    "creator": {
        "price_usd": 95, "videos_per_month": 5, "seconds_per_video": 30,
        "includes_aria_script": True, "includes_brand_voice_review": True,
        "includes_dedicated_agent": False,
    },
    "cinematic_pro": {
        "price_usd": 125, "videos_per_month": 3, "seconds_per_video": 60,
        "includes_aria_script": True, "includes_brand_voice_review": True,
        "includes_dedicated_agent": True,
    },
}
VIDEO_PACK_ENTITLEMENTS: Final[MappingProxyType] = MappingProxyType({
    k: MappingProxyType(v) for k, v in _PACK_DATA.items()
})

VIDEO_PACK_CODES: Final[FrozenSet[str]] = frozenset(_PACK_DATA.keys())
PLAN_CODES: Final[FrozenSet[str]] = frozenset(_PLAN_BASE.keys())


def get_pack(code: str) -> MappingProxyType:
    """Lookup pack por code. KeyError si no existe."""
    return VIDEO_PACK_ENTITLEMENTS[code]


def get_plan_base(plan: str) -> MappingProxyType:
    """Lookup base de video incluida en el plan. KeyError si plan inválido."""
    return VIDEO_PLAN_INCLUDED[plan]


def is_pack_available_for_plan(plan: str) -> bool:
    """Packs disponibles solo en basic y pro · NO en adopcion (§4.4)."""
    return plan in {"basic", "pro"}


# Self-check al import (fail-fast · patrón limits_omega.py · sin pytest infra)
assert VIDEO_PLAN_INCLUDED["basic"]["videos"] == 1, "basic cebo debe ser 1×8s lifetime"
assert VIDEO_PLAN_INCLUDED["pro"]["videos"] == 2, "pro base debe ser 2×8s monthly"
assert get_pack("starter")["price_usd"] == 39
assert get_pack("creator")["seconds_per_video"] == 30
assert get_pack("cinematic_pro")["includes_dedicated_agent"] is True
assert not is_pack_available_for_plan("adopcion"), "Packs NO en Adopción"
# Frozen: MappingProxyType es read-only por definición (outer + inner)
assert isinstance(VIDEO_PACK_ENTITLEMENTS, MappingProxyType)
assert isinstance(VIDEO_PACK_ENTITLEMENTS["starter"], MappingProxyType)
