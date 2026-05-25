"""GUARDIAN · modelo de amenazas de sesión · capa pura (A2). Heurística Capa 1.

Spec: GUARDIAN_SECURITY_AGENT.md (firmado 24 may 2026 · gitignored). risk_score 0-100.
impossible_travel v1 = proxy geo-free (IPs distintas en ventana) · geo real → fase posterior.
Cero imports externos.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Final, Optional, Tuple

BRUTE_FORCE_MAX_FAILS: Final = 5
BRUTE_FORCE_WINDOW_MIN: Final = 15
IMPOSSIBLE_TRAVEL_WINDOW_MIN: Final = 5


class SessionAction(Enum):
    ALLOW = "allow"; CHALLENGE = "challenge"; FLAG = "flag"; BLOCK = "block"


class SecuritySignal(Enum):
    BRUTE_FORCE = "brute_force"; IMPOSSIBLE_TRAVEL = "impossible_travel"
    NEW_DEVICE = "new_device"; WATCHLIST_BLOCK = "watchlist_block"; WATCHLIST_WATCH = "watchlist_watch"


@dataclass(frozen=True)
class LoginContext:
    user_id: str
    ip: str
    user_agent: str
    at: datetime
    success: bool


@dataclass(frozen=True)
class SecurityEvent:
    event_type: str
    ip: str
    user_agent: str
    at: datetime


@dataclass(frozen=True)
class SessionAssessment:
    action: SessionAction
    risk_score: int
    signals: Tuple[SecuritySignal, ...]
    incident_type: Optional[str]


def _fails_in_window(recent: Tuple[SecurityEvent, ...], now: datetime) -> int:
    cutoff = now - timedelta(minutes=BRUTE_FORCE_WINDOW_MIN)
    return sum(1 for e in recent if e.event_type == "login_failed" and e.at >= cutoff)


def _distinct_recent_login_ips(recent: Tuple[SecurityEvent, ...], now: datetime, ip: str) -> int:
    cutoff = now - timedelta(minutes=IMPOSSIBLE_TRAVEL_WINDOW_MIN)
    ips = {e.ip for e in recent if e.event_type == "login_success" and e.at >= cutoff}
    ips.add(ip)
    return len(ips)


def _is_new_ip(recent: Tuple[SecurityEvent, ...], ip: str) -> bool:
    return ip not in {e.ip for e in recent if e.event_type == "login_success"}


def analyze(current: LoginContext, recent: Tuple[SecurityEvent, ...],
            watchlist: Optional[str]) -> SessionAssessment:
    """Señales → acción. Auto-BLOCK SOLO determinístico (brute_force + watchlist block · §7.3)."""
    if watchlist == "allow":
        return SessionAssessment(SessionAction.ALLOW, 0, (), None)
    if watchlist == "block":
        return SessionAssessment(SessionAction.BLOCK, 95, (SecuritySignal.WATCHLIST_BLOCK,), "anomalous_session")
    fails = _fails_in_window(recent, current.at) + (0 if current.success else 1)
    if fails >= BRUTE_FORCE_MAX_FAILS:
        return SessionAssessment(SessionAction.BLOCK, 90, (SecuritySignal.BRUTE_FORCE,), "brute_force")
    if current.success and _distinct_recent_login_ips(recent, current.at, current.ip) >= 2:
        return SessionAssessment(SessionAction.CHALLENGE, 70, (SecuritySignal.IMPOSSIBLE_TRAVEL,), "impossible_travel")
    if watchlist == "watch":
        return SessionAssessment(SessionAction.FLAG, 60, (SecuritySignal.WATCHLIST_WATCH,), "anomalous_session")
    if current.success and _is_new_ip(recent, current.ip):
        return SessionAssessment(SessionAction.FLAG, 30, (SecuritySignal.NEW_DEVICE,), None)
    return SessionAssessment(SessionAction.ALLOW, 0, (), None)
