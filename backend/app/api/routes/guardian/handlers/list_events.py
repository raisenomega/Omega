"""GET /guardian/events · user_security_log con campos ricos + filtro · owner-only (operador global)."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.infrastructure.supabase_service import get_supabase_service


async def handle_list_events(authorization: Optional[str], event_type: Optional[str] = None,
                             limit: int = 50) -> Dict[str, Any]:
    await require_superadmin(authorization)
    q = (get_supabase_service().client.table("user_security_log")
         .select("id, user_id, event_type, ip_address, user_agent, country, geo, session_id, risk_score, created_at")
         .order("created_at", desc=True).limit(min(limit, 100)))
    if event_type:
        q = q.eq("event_type", event_type)
    return {"events": q.execute().data or []}
