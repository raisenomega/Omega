"""POST /guardian/login-event · dispara GUARDIAN analyzer post-login (4B-3).

El frontend lo llama tras un intento de login Supabase (éxito o fallo). El backend
deriva user_id (JWT), ip (request) y user_agent (header). Fail-open: si GUARDIAN
falla → action='allow' (el login no se bloquea · §7.4).
"""
import asyncio
import logging
from typing import Optional
from fastapi import Request
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.guardian.models import LoginEventRequest, LoginEventResponse
from app.bc_cognition.application.guardian_session_analyzer import analyze_login

logger = logging.getLogger(__name__)


def client_ip(request: Request) -> str:
    """IP del cliente · respeta X-Forwarded-For (Railway/proxy) · fallback request.client."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else ""


async def handle_login_event(
    request: Request, body: LoginEventRequest, authorization: Optional[str],
) -> LoginEventResponse:
    user = await get_current_user(authorization)
    assessment, err = await asyncio.to_thread(
        analyze_login, str(user["id"]), client_ip(request),
        request.headers.get("user-agent", ""), body.success,
    )
    if err is not None or assessment is None:
        return LoginEventResponse(action="allow", risk_score=0, signals=[])  # fail-open §7.4
    return LoginEventResponse(
        action=assessment.action.value, risk_score=assessment.risk_score,
        signals=[s.value for s in assessment.signals],
    )
