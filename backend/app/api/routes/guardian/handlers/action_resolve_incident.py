"""POST /guardian/actions/resolve-incident · marca incidente resolved O false_positive · owner-only.

Consolida 2 acciones del modal ([Resolver] / [Falso positivo]) en 1 endpoint con flag false_positive
(misma UPDATE · solo cambia status). DRY · la UI llama con el flag correspondiente.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.guardian.models import ResolveIncidentRequest
from app.infrastructure.supabase_service import get_supabase_service


async def handle_resolve_incident(body: ResolveIncidentRequest, authorization: Optional[str]) -> Dict[str, Any]:
    user = await require_superadmin(authorization)
    status = "false_positive" if body.false_positive else "resolved"
    upd = get_supabase_service().client.table("security_incidents").update({
        "status": status, "resolved_at": datetime.now(timezone.utc).isoformat(),
        "resolved_by": user["id"], "resolution_notes": body.resolution_notes,
    }).eq("id", body.incident_id).execute()
    return {"success": bool(upd.data), "incident_id": body.incident_id, "status": status}
