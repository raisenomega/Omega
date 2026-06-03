"""SENTINEL Capa 9 · estado de observabilidad runtime para el panel · owner-only."""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin


async def handle_runtime_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan + resumen 24h (errores backend/frontend + top signatures recurrentes)."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    last = (sb.table("sentinel_runtime_scans").select("*")
            .order("created_at", desc=True).limit(1).execute().data or [None])[0]
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    be = sb.table("backend_error_log").select("id", count="exact").gte("created_at", since).execute()
    fe = (sb.table("frontend_error_log").select("signature,message").gte("created_at", since).execute().data) or []

    counts: Dict[str, Dict[str, Any]] = {}
    for r in fe:
        sig = r.get("signature") or "?"
        c = counts.setdefault(sig, {"signature": sig[:16], "message": (r.get("message") or "")[:100], "count": 0})
        c["count"] += 1
    top = sorted(counts.values(), key=lambda x: x["count"], reverse=True)[:5]

    return {
        "last_scan": last,
        "last_24h": {
            "total_errors_backend": be.count or 0,
            "total_errors_frontend": len(fe),
            "top_signatures": top,
        },
        "coverage": {"railway_api_active": False, "reason": "Railway logs no integrado (V1)"},
    }
