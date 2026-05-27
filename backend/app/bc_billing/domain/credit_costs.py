"""DEBT-052 · costos de crédito por generación + tiers de CREDIT PACK.

Capa de dominio PURA (constantes + helpers · sin I/O · A2). Los CREDIT PACKS son
OPCIONALES y SEPARADOS del plan base ($29/$65/$199) y de los VIDEO PACKS (§4.4):
dan créditos EXTRA de API para más generaciones de TEXTO/IMAGEN. El video se
consume vía Video Packs aparte (DEBT-VID-001 · NO toca estos créditos).

Costo OMEGA por imagen derivado de MODELO_NEGOCIO §4.4 (Enterprise ~$15/300 imgs
≈ $0.05). Claude usa el cost_usd que ya computa anthropic_adapter (estimate_cost).
NO modifica limits_omega · MAX_USD_DIARIO sigue siendo el techo diario (G1).
"""
from typing import Final

# Credit packs (opcional · extra · separado de plan base y video packs).
# Budget mensual de créditos de API (USD) · decisión owner 26 may 2026.
PACK_BUDGETS_USD: Final[dict[str, float]] = {
    "micro": 9.0,
    "starter": 25.0,
    "plus": 59.0,
    "ultra": 119.0,
}

# Costo OMEGA por imagen (Nano Banana) · §4.4: Enterprise ~$15 / 300 imgs ≈ $0.05.
_IMAGE_COST_USD: Final[dict[str, float]] = {
    "default": 0.05,
    "premium": 0.10,   # gemini-3-pro-image · brand-critical
    "cheap": 0.03,
}

# Auto-recarga: saldo ≤ 20% → consumido ≥ 80% del budget (toggle · decisión owner).
RECHARGE_THRESHOLD: Final[float] = 0.80


def pack_budget_usd(tier: str) -> float:
    """Budget mensual USD del credit pack · 0 si tier desconocido."""
    return PACK_BUDGETS_USD.get(tier, 0.0)


def cost_for_image(route: str = "default") -> float:
    """Costo USD por imagen generada (Nano Banana) según route."""
    return _IMAGE_COST_USD.get(route, _IMAGE_COST_USD["default"])
