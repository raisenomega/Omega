"""GUARDIAN · use case: analiza un login, persiste log + incidente (A9).

Spec: GUARDIAN_SECURITY_AGENT.md §2/§6. Result-tuple (A5) · fail-open (§7.4):
ante error retorna GuardianError y el caller (login) NO bloquea el acceso.
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple
from app.bc_cognition.domain.guardian_threats import (
    LoginContext, SessionAction, SessionAssessment, analyze,
)
from app.bc_cognition.infrastructure import guardian_repository as repo
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GuardianError:
    code: str
    detail: str


def _severity_for(risk: int) -> str:
    if risk >= 90:
        return "critical"
    if risk >= 70:
        return "high"
    if risk >= 40:
        return "medium"
    return "low"


def analyze_login(
    user_id: str, ip: str, user_agent: str, success: bool,
) -> Tuple[Optional[SessionAssessment], Optional[GuardianError]]:
    """Punto único GUARDIAN de login. Cero raise (A5). Fail-open: error → caller permite login."""
    try:
        supabase = get_supabase_service()
        ctx = LoginContext(user_id, ip, user_agent, datetime.now(timezone.utc), success)
        recent = repo.fetch_recent_events(supabase, user_id)
        watchlist = repo.lookup_ip(supabase, ip)
        a = analyze(ctx, recent, watchlist)
        signals = [s.value for s in a.signals]
        repo.insert_security_log(
            supabase, user_id, ip, user_agent,
            "login_success" if success else "login_failed", a.risk_score, signals,
        )
        if a.action != SessionAction.ALLOW and a.incident_type:
            repo.insert_incident(supabase, user_id, a.incident_type, _severity_for(a.risk_score), signals)
        return a, None
    except Exception as exc:  # fail-open (§7.4) · login no se bloquea si GUARDIAN rompe
        logger.error(f"guardian analyze_login failed (user={user_id}): {exc}", exc_info=True)
        return None, GuardianError("guardian_failure", str(exc))
