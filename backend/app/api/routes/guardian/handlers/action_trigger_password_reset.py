"""POST /guardian/actions/trigger-password-reset · Supabase manda el recovery email · owner-only.

Usa reset_password_for_email (template default Supabase · cero Resend manual ·
DEBT-GUARDIAN-PASSWORD-RESET-CUSTOM-TEMPLATE para branding OMEGA).
"""
import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException

from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.guardian.models import PasswordResetRequest
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_trigger_password_reset(body: PasswordResetRequest, authorization: Optional[str]) -> Dict[str, Any]:
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    try:
        u = sb.auth.admin.get_user_by_id(body.user_id)
        email = getattr(getattr(u, "user", None), "email", None)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=404, detail=f"user_not_found:{e}")
    if not email:
        raise HTTPException(status_code=400, detail="user_sin_email")
    sb.auth.reset_password_for_email(email)  # Supabase envía el recovery email
    sb.table("user_security_log").insert({
        "user_id": body.user_id, "event_type": "password_reset",
        "metadata": {"action": "password_reset_by_owner", "reason": body.reason},
    }).execute()
    if body.incident_id:
        sb.table("security_incidents").update(
            {"resolution_notes": "Triggered password reset"}).eq("id", body.incident_id).execute()
    return {"success": True, "recovery_email_sent": True}
