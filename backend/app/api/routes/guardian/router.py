"""GUARDIAN router · seguridad usuario/sesión (4B-3).

POST /guardian/login-event   · trigger del analyzer post-login (el frontend lo llama)
GET  /guardian/session-report · resumen de la cuenta para SecurityKPICard
"""
from typing import Optional
from fastapi import APIRouter, Header, Query, Request
from app.api.routes.guardian.handlers import (
    handle_login_event, handle_session_report,
    handle_block_ip, handle_force_logout, handle_resolve_incident, handle_trigger_password_reset,
    handle_list_events, handle_list_incidents, handle_list_watchlist, handle_user_detail,
    handle_consult_incident,
)
from app.api.routes.guardian.models import (
    LoginEventRequest, LoginEventResponse, SessionReportResponse,
    BlockIpRequest, ForceLogoutRequest, ResolveIncidentRequest, PasswordResetRequest, ConsultRequest,
)

router = APIRouter(prefix="/guardian", tags=["GUARDIAN 🛡️"])


@router.post("/login-event", response_model=LoginEventResponse)
async def login_event(
    body: LoginEventRequest, request: Request, authorization: Optional[str] = Header(None),
) -> LoginEventResponse:
    return await handle_login_event(request, body, authorization)


@router.get("/session-report", response_model=SessionReportResponse)
async def session_report(authorization: Optional[str] = Header(None)) -> SessionReportResponse:
    return await handle_session_report(authorization)


# ── GET filtrados para el panel (4B-4 · owner-only) ──
@router.get("/events")
async def list_events(event_type: Optional[str] = Query(None), limit: int = Query(50),
                      authorization: Optional[str] = Header(None)):
    return await handle_list_events(authorization, event_type, limit)


@router.get("/incidents")
async def list_incidents(status: Optional[str] = Query(None), severity: Optional[str] = Query(None),
                         limit: int = Query(50), authorization: Optional[str] = Header(None)):
    return await handle_list_incidents(authorization, status, severity, limit)


@router.get("/watchlist")
async def list_watchlist(list_type: Optional[str] = Query(None), active_only: bool = Query(False),
                         authorization: Optional[str] = Header(None)):
    return await handle_list_watchlist(authorization, list_type, active_only)


@router.get("/user-detail/{user_id}")
async def user_detail(user_id: str, authorization: Optional[str] = Header(None)):
    return await handle_user_detail(user_id, authorization)


# ── Acciones owner end-to-end (4B-1 · gated require_superadmin) ──
@router.post("/actions/block-ip")
async def block_ip(body: BlockIpRequest, authorization: Optional[str] = Header(None)):
    return await handle_block_ip(body, authorization)


@router.post("/actions/force-logout")
async def force_logout(body: ForceLogoutRequest, authorization: Optional[str] = Header(None)):
    return await handle_force_logout(body, authorization)


@router.post("/actions/resolve-incident")
async def resolve_incident(body: ResolveIncidentRequest, authorization: Optional[str] = Header(None)):
    return await handle_resolve_incident(body, authorization)


@router.post("/actions/trigger-password-reset")
async def trigger_password_reset(body: PasswordResetRequest, authorization: Optional[str] = Header(None)):
    return await handle_trigger_password_reset(body, authorization)


@router.post("/consult/incident")
async def consult_incident(body: ConsultRequest, authorization: Optional[str] = Header(None)):
    return await handle_consult_incident(body, authorization)
