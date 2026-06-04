"""POST /guardian/actions/block-ip · INSERT ip_watchlist (block) + opcional resolver incidente · owner-only."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.guardian.models import BlockIpRequest
from app.infrastructure.supabase_service import get_supabase_service


async def handle_block_ip(body: BlockIpRequest, authorization: Optional[str]) -> Dict[str, Any]:
    user = await require_superadmin(authorization)
    sb = get_supabase_service().client
    ins = sb.table("ip_watchlist").insert({
        "ip_address": body.ip_address, "list_type": "block", "reason": body.reason,
        "scope_client_id": body.scope_client_id, "expires_at": body.expires_at, "created_by": user["id"],
    }).execute()
    wl_id = (ins.data or [{}])[0].get("id")
    incident_updated = False
    if body.incident_id:
        sb.table("security_incidents").update({
            "status": "resolved", "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": user["id"], "resolution_notes": f"IP {body.ip_address} bloqueada",
        }).eq("id", body.incident_id).execute()
        incident_updated = True
    sb.table("user_security_log").insert({
        "user_id": user["id"], "event_type": "suspicious_activity", "ip_address": body.ip_address,
        "metadata": {"action": "block_ip_by_owner", "reason": body.reason},
    }).execute()
    return {"success": True, "ip_watchlist_id": wl_id, "incident_updated": incident_updated}
