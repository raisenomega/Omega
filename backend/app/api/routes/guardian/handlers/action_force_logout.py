"""POST /guardian/actions/force-logout · revoca TODAS las sesiones del user · owner-only.

sign_out(jwt) toma token (no user_id) → se usa el endpoint GoTrue admin /logout vía httpx + service key.
Fallback (DEBT-GUARDIAN-FORCE-LOGOUT-FALLBACK): ban 24h vía update_user_by_id si el REST no responde 2xx.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import httpx

from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.guardian.models import ForceLogoutRequest
from app.config import settings
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_force_logout(body: ForceLogoutRequest, authorization: Optional[str]) -> Dict[str, Any]:
    user = await require_superadmin(authorization)
    key = settings.supabase_service_role_key
    method, ok = "gotrue_admin_logout", False
    try:
        r = httpx.post(f"{settings.supabase_url}/auth/v1/admin/users/{body.user_id}/logout",
                       headers={"Authorization": f"Bearer {key}", "apikey": key}, timeout=8.0)
        ok = r.status_code in (200, 204)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"force_logout REST failed: {e}")
    if not ok:  # fallback · ban temporal
        try:
            get_supabase_service().client.auth.admin.update_user_by_id(body.user_id, {"ban_duration": "24h"})
            method, ok = "ban_24h_fallback", True
        except Exception as e:  # noqa: BLE001
            logger.error(f"force_logout fallback failed: {e}")
            return {"success": False, "detail": "logout REST y ban fallaron"}
    sb = get_supabase_service().client
    sb.table("user_security_log").insert({
        "user_id": body.user_id, "event_type": "logout",
        "metadata": {"action": "force_logout_by_owner", "method": method, "reason": body.reason},
    }).execute()
    if body.incident_id:
        sb.table("security_incidents").update({
            "status": "resolved", "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": user["id"], "resolution_notes": f"Force logout ({method})",
        }).eq("id", body.incident_id).execute()
    return {"success": True, "method": method}
