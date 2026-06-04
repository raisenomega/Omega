"""GET /guardian/watchlist · ip_watchlist con filtro list_type/active · owner-only."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.infrastructure.supabase_service import get_supabase_service


async def handle_list_watchlist(authorization: Optional[str], list_type: Optional[str] = None,
                                active_only: bool = False) -> Dict[str, Any]:
    await require_superadmin(authorization)
    q = (get_supabase_service().client.table("ip_watchlist")
         .select("id, ip_address, list_type, reason, scope_client_id, created_by, expires_at, created_at")
         .order("created_at", desc=True).limit(100))
    if list_type:
        q = q.eq("list_type", list_type)
    rows = q.execute().data or []
    if active_only:  # vigente = sin expires_at o futuro
        now = datetime.now(timezone.utc).isoformat()
        rows = [r for r in rows if not r.get("expires_at") or r["expires_at"] > now]
    return {"watchlist": rows}
