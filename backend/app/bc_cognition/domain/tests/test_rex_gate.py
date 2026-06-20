"""Tests del gate REX (F1) · 7 holds + publish + boundaries + orden de prioridad.

Umbrales leídos de LIMITS_OMEGA / X5 (no hardcodeados · si cambian, el test sigue).
"""
from typing import Optional

from app.bc_cognition.domain.limits_omega import LIMITS_OMEGA
from app.bc_cognition.domain.brand_voice_scorer_prompt import SCORE_BRAND_BAR
from app.bc_cognition.domain.rex_gate import RexGateInput, evaluate_rex_gate

_MIN_CONF: int = LIMITS_OMEGA["MIN_CONFIDENCE_TO_ACT"]
_MAX_POSTS: int = LIMITS_OMEGA["MAX_POSTS_AUTO_PER_DIA_CLIENTE"]


def _ok(
    addon_active: bool = True,
    toggle_on: bool = True,
    crisis_active: bool = False,
    brand_voice_score: Optional[float] = SCORE_BRAND_BAR,
    confidence: int = _MIN_CONF,
    posts_today: int = 0,
    has_media: bool = True,
    connection_valid: bool = True,
) -> RexGateInput:
    """Input que PASA los 7 checks · override UN campo para forzar un hold."""
    return RexGateInput(
        addon_active=addon_active, toggle_on=toggle_on, crisis_active=crisis_active,
        brand_voice_score=brand_voice_score, confidence=confidence,
        posts_today=posts_today, has_media=has_media, connection_valid=connection_valid,
    )


# ── publish feliz ────────────────────────────────────────────────────
def test_publish_happy() -> None:
    assert evaluate_rex_gate(_ok()).decision == "publish"


# ── 7 holds (uno por check) ──────────────────────────────────────────
def test_hold_gating_off() -> None:
    assert evaluate_rex_gate(_ok(addon_active=False)).reason == "gating_off"
    assert evaluate_rex_gate(_ok(toggle_on=False)).reason == "gating_off"


def test_hold_crisis_active() -> None:
    v = evaluate_rex_gate(_ok(crisis_active=True))
    assert v.decision == "hold" and v.reason == "crisis_active"


def test_hold_brand_voice_below_bar() -> None:
    assert evaluate_rex_gate(_ok(brand_voice_score=SCORE_BRAND_BAR - 0.01)).reason == "brand_voice_below_bar"


def test_hold_brand_voice_none() -> None:
    assert evaluate_rex_gate(_ok(brand_voice_score=None)).reason == "brand_voice_below_bar"


def test_hold_low_confidence() -> None:
    assert evaluate_rex_gate(_ok(confidence=_MIN_CONF - 1)).reason == "low_confidence"


def test_hold_daily_limit() -> None:
    assert evaluate_rex_gate(_ok(posts_today=_MAX_POSTS)).reason == "daily_limit_reached"


def test_hold_no_media() -> None:
    assert evaluate_rex_gate(_ok(has_media=False)).reason == "no_media"


def test_hold_connection_invalid() -> None:
    assert evaluate_rex_gate(_ok(connection_valid=False)).reason == "connection_invalid"


# ── boundaries ───────────────────────────────────────────────────────
def test_confidence_boundary() -> None:
    assert evaluate_rex_gate(_ok(confidence=_MIN_CONF)).decision == "publish"       # 7 pasa
    assert evaluate_rex_gate(_ok(confidence=_MIN_CONF - 1)).decision == "hold"      # 6 hold


def test_posts_boundary() -> None:
    assert evaluate_rex_gate(_ok(posts_today=_MAX_POSTS - 1)).decision == "publish"  # 2 pasa
    assert evaluate_rex_gate(_ok(posts_today=_MAX_POSTS)).decision == "hold"         # 3 hold


def test_brand_voice_boundary() -> None:
    assert evaluate_rex_gate(_ok(brand_voice_score=SCORE_BRAND_BAR)).decision == "publish"       # 0.70 pasa
    assert evaluate_rex_gate(_ok(brand_voice_score=SCORE_BRAND_BAR - 0.01)).decision == "hold"   # 0.69 hold


# ── orden de prioridad (el primer check que falla manda) ─────────────
def test_priority_order() -> None:
    # gating gana sobre crisis
    assert evaluate_rex_gate(_ok(addon_active=False, crisis_active=True)).reason == "gating_off"
    # crisis gana sobre brand voice
    assert evaluate_rex_gate(_ok(crisis_active=True, brand_voice_score=None)).reason == "crisis_active"
    # brand voice gana sobre confidence
    assert evaluate_rex_gate(_ok(brand_voice_score=None, confidence=0)).reason == "brand_voice_below_bar"
