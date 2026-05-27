"""DEBT-052 · costos de crédito por generación + tiers de pack prepagado.

Capa de dominio PURA (constantes + helpers · sin I/O · A2). Costos REALES
derivados de MODELO_NEGOCIO §4.4 (costo OMEGA por generación). Claude usa el
cost_usd que ya computa anthropic_adapter (estimate_cost); imagen/video usan
estos fijos. NO modifica limits_omega · MAX_USD_DIARIO_API_POR_CLIENTE sigue
siendo el techo diario inmutable (circuit-breaker · G1) · esto es la capa de
créditos prepagados por encima.
"""
from typing import Final

# Tiers de pack prepagado (budget mensual USD) · decisión owner 26 may 2026.
PACK_BUDGETS_USD: Final[dict[str, float]] = {
    "starter": 15.0,
    "plus": 49.0,
    "pro": 99.0,
    "ultra": 199.0,
}

# Costo OMEGA por imagen (Nano Banana) · §4.4: Enterprise ~$15 / 300 imgs ≈ $0.05.
_IMAGE_COST_USD: Final[dict[str, float]] = {
    "default": 0.05,
    "premium": 0.10,   # gemini-3-pro-image · brand-critical
    "cheap": 0.03,
}

# Costo OMEGA por video (Veo 3.1) por duración · §4.4: 8s≈$2 · 30s≈$5 · 60s≈$8.
_VIDEO_COST_USD: Final[dict[int, float]] = {8: 2.0, 30: 5.0, 60: 8.0}
_VIDEO_COST_PER_SEC: Final[float] = 0.25  # fallback duraciones no tabuladas

# Auto-recarga: saldo ≤ 20% → consumido ≥ 80% del budget (toggle · decisión owner).
RECHARGE_THRESHOLD: Final[float] = 0.80


def pack_budget_usd(tier: str) -> float:
    """Budget mensual USD del tier de pack · 0 si tier desconocido."""
    return PACK_BUDGETS_USD.get(tier, 0.0)


def cost_for_image(route: str = "default") -> float:
    """Costo USD por imagen generada (Nano Banana) según route."""
    return _IMAGE_COST_USD.get(route, _IMAGE_COST_USD["default"])


def cost_for_video(duration_s: int) -> float:
    """Costo USD por video generado (Veo 3.1) según duración."""
    exact = _VIDEO_COST_USD.get(duration_s)
    return exact if exact is not None else round(duration_s * _VIDEO_COST_PER_SEC, 4)
