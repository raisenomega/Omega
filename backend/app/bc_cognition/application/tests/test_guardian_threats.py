"""Tests dominio guardian_threats · 4 casos (happy/edge/error/boundary). Spec §2."""
from datetime import datetime, timedelta, timezone
from app.bc_cognition.domain.guardian_threats import (
    LoginContext, SecurityEvent, SessionAction, SecuritySignal, analyze,
)

_NOW = datetime(2026, 5, 24, 12, 0, tzinfo=timezone.utc)


def _ctx(ip: str = "1.1.1.1", success: bool = True) -> LoginContext:
    return LoginContext("u1", ip, "ua", _NOW, success)


def _fail(mins: int, ip: str = "9.9.9.9") -> SecurityEvent:
    return SecurityEvent("login_failed", ip, "ua", _NOW - timedelta(minutes=mins))


def _ok(mins: int, ip: str) -> SecurityEvent:
    return SecurityEvent("login_success", ip, "ua", _NOW - timedelta(minutes=mins))


def test_happy_clean_login_allow():
    """IP conocida, sin fallos, sin watchlist → ALLOW risk 0."""
    a = analyze(_ctx("1.1.1.1"), (_ok(60, "1.1.1.1"),), None)
    assert a.action == SessionAction.ALLOW and a.risk_score == 0 and a.signals == ()


def test_edge_new_device_flag():
    """Login exitoso desde IP nunca vista → NEW_DEVICE → FLAG risk 30."""
    a = analyze(_ctx("2.2.2.2"), (_ok(60, "1.1.1.1"),), None)
    assert a.action == SessionAction.FLAG and SecuritySignal.NEW_DEVICE in a.signals and a.risk_score == 30


def test_error_brute_force_block():
    """5 login_failed en ventana → BRUTE_FORCE → BLOCK (determinístico · §7.3)."""
    a = analyze(_ctx(success=False), tuple(_fail(m) for m in (1, 2, 3, 4, 5)), None)
    assert a.action == SessionAction.BLOCK and a.incident_type == "brute_force" and a.risk_score >= 90


def test_boundary_threshold_and_impossible_travel():
    """Umbral exacto brute_force + proxy impossible_travel (2 IPs/5min)."""
    # 3 fails previos + current fail = 4 → NO block
    assert analyze(_ctx("1.1.1.1", False), tuple(_fail(m) for m in (1, 2, 3)), None).action != SessionAction.BLOCK
    # 4 fails previos + current fail = 5 → BLOCK
    assert analyze(_ctx("1.1.1.1", False), tuple(_fail(m) for m in (1, 2, 3, 4)), None).action == SessionAction.BLOCK
    # 2 IPs exitosas distintas en 5 min → CHALLENGE
    a = analyze(_ctx("6.6.6.6", True), (_ok(2, "5.5.5.5"),), None)
    assert a.action == SessionAction.CHALLENGE and SecuritySignal.IMPOSSIBLE_TRAVEL in a.signals
