"""GUARDIAN router · seguridad usuario/sesión (4B-3).

POST /guardian/login-event   · trigger del analyzer post-login (el frontend lo llama)
GET  /guardian/session-report · resumen de la cuenta para SecurityKPICard
"""
from typing import Optional
from fastapi import APIRouter, Header, Request
from app.api.routes.guardian.handlers import handle_login_event, handle_session_report
from app.api.routes.guardian.models import (
    LoginEventRequest, LoginEventResponse, SessionReportResponse,
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
