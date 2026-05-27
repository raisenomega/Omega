"""GET /security-dev/guardian · logs + incidents + watchlist (owner ve TODO).

Columnas alineadas al esquema real (migración 00022):
  · security_incidents → temporal es `detected_at` (NO existe created_at).
  · ip_watchlist       → clasificación es `list_type` block/allow/watch (NO risk_level).
"""
import logging
from typing import Optional, Dict, Any
from app.api.routes.auth.super_owner import require_super_owner
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_guardian_data(authorization: Optional[str]) -> Dict[str, Any]:
    """Owner ve TODOS los eventos (no scoped por user_id · es el operador global)."""
    await require_super_owner(authorization)
    sb = get_supabase_service().client
    try:
        logs_r = sb.table("user_security_log") \
            .select("id, event_type, ip_address, user_agent, risk_score, created_at") \
            .order("created_at", desc=True).limit(50).execute()
        incidents_r = sb.table("security_incidents") \
            .select("id, incident_type, severity, status, detected_at") \
            .order("detected_at", desc=True).limit(20).execute()
        watchlist_r = sb.table("ip_watchlist") \
            .select("id, ip_address, list_type, reason, created_at") \
            .order("created_at", desc=True).limit(20).execute()
        return {
            "logs":      logs_r.data or [],
            "incidents": incidents_r.data or [],
            "watchlist": watchlist_r.data or [],
        }
    except Exception as e:
        logger.error(f"handle_guardian_data failed: {e}", exc_info=True)
        return {"logs": [], "incidents": [], "watchlist": [], "error": str(e)}
