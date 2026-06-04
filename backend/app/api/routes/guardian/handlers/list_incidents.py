"""GET /guardian/incidents · security_incidents con filtro status/severity · owner-only."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.infrastructure.supabase_service import get_supabase_service


async def handle_list_incidents(authorization: Optional[str], status: Optional[str] = None,
                                severity: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    await require_superadmin(authorization)
    q = (get_supabase_service().client.table("security_incidents")
         .select("id, user_id, incident_type, severity, status, summary, evidence, "
                 "detected_at, resolved_at, resolved_by, resolution_notes")
         .order("detected_at", desc=True).limit(min(limit, 100)))
    if status:
        q = q.eq("status", status)
    if severity:
        q = q.eq("severity", severity)
    return {"incidents": q.execute().data or []}
