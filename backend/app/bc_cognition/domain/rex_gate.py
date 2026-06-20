"""REX · gate de seguridad determinístico para publicación autónoma (DEBT-098 · F1).

Función PURA (A2 · sin I/O · sin imports de infra/api). El use case resuelve los
datos y este gate decide publish | hold con reason determinística. Los 7 checks
van en ORDEN DE PRIORIDAD: el PRIMERO que falla manda. Umbrales leídos de
LIMITS_OMEGA / X5 (no se hardcodean ni se duplican).
"""
from dataclasses import dataclass
from typing import Final, Literal, Optional

from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA
from app.bc_cognition.domain.brand_voice_scorer_prompt import SCORE_BRAND_BAR

_MIN_CONFIDENCE: Final[int] = LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"]          # P3 · = 7
_MAX_POSTS_DAY: Final[int] = LIMITS_OMEGA["MAX_POSTS_AUTO_PER_DIA_CLIENTE"]  # anti-saturación · = 3


@dataclass(frozen=True)
class RexGateInput:
    """Datos YA resueltos por el use case (cero I/O en el gate)."""
    addon_active: bool          # ¿compró el add-on Modo Autónomo?
    toggle_on: bool             # ¿el humano encendió el toggle? (consentimiento)
    crisis_active: bool         # kill-switch manual de crisis del cliente
    brand_voice_score: Optional[float]  # X5 · None = sin referencia/medición
    confidence: int             # convicción del draft (0-10)
    posts_today: int            # publicaciones auto ya hechas hoy por el cliente
    has_media: bool             # requisito de media de la plataforma satisfecho
    connection_valid: bool      # token/cuenta de la red válidos


@dataclass(frozen=True)
class RexVerdict:
    decision: Literal["publish", "hold"]
    reason: Optional[str] = None


def evaluate_rex_gate(ctx: RexGateInput) -> RexVerdict:
    """7 checks en orden de prioridad · primer fallo → hold(reason) · todos OK → publish."""
    # 1 · Gating: comprado + toggle humano encendido
    if not (ctx.addon_active and ctx.toggle_on):
        return RexVerdict("hold", "gating_off")
    # 2 · Kill-switch manual de crisis (P4 · congela TODAS las publicaciones del cliente)
    if ctx.crisis_active:
        return RexVerdict("hold", "crisis_active")
    # 3 · Brand voice limpio (X5 · REX exige >= bar · más estricto que el below_bar humano)
    if ctx.brand_voice_score is None or ctx.brand_voice_score < SCORE_BRAND_BAR:
        return RexVerdict("hold", "brand_voice_below_bar")
    # 4 · Convicción mínima (P3)
    if ctx.confidence < _MIN_CONFIDENCE:
        return RexVerdict("hold", "low_confidence")
    # 5 · Límite diario de posts automáticos
    if ctx.posts_today >= _MAX_POSTS_DAY:
        return RexVerdict("hold", "daily_limit_reached")
    # 6 · Media presente (el use case resuelve el requisito por plataforma)
    if not ctx.has_media:
        return RexVerdict("hold", "no_media")
    # 7 · Conexión/token de la cuenta válidos
    if not ctx.connection_valid:
        return RexVerdict("hold", "connection_invalid")
    return RexVerdict("publish")
