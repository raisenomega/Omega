"""SENTINEL Capa 11 · estado de integraciones para el panel · owner-only."""
from typing import Dict, Any, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin


async def handle_integrations_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan + promedio 24h."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    rows = (sb.table("sentinel_integrations_scans").select("*")
            .order("created_at", desc=True).limit(24).execute().data) or []
    return {
        "last_scan": rows[0] if rows else None,
        "last_24h_avg_score": round(sum(r["score"] for r in rows) / len(rows)) if rows else None,
    }
