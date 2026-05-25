"""GET /guardian/session-report · resumen de seguridad de la cuenta (SecurityKPICard · 4B-3).

Read-only · scoped por JWT (RLS garantiza que el user solo ve lo suyo). Empty state
honesto si no hay eventos (tablas vacías hasta db push + primer login-event).
"""
import asyncio
from typing import Optional
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.guardian.models import SessionReportResponse
from app.bc_cognition.infrastructure import guardian_repository as repo
from app.infrastructure.supabase_service import get_supabase_service


async def handle_session_report(authorization: Optional[str]) -> SessionReportResponse:
    user = await get_current_user(authorization)
    summary = await asyncio.to_thread(
        repo.fetch_session_summary, get_supabase_service(), str(user["id"]),
    )
    return SessionReportResponse(**summary)
