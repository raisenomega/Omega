"""SENTINEL Capa 12 · estado de salud de agentes IA para el panel · owner-only."""
from typing import Dict, Any, Optional, List

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin


async def handle_agents_health_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan + summary agregado."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    last = (sb.table("sentinel_agents_health_scans").select("*")
            .order("created_at", desc=True).limit(1).execute().data or [None])[0]
    per: List[Dict[str, Any]] = (last or {}).get("per_agent", []) if last else []
    srs = [a["success_rate"] for a in per if a.get("success_rate") is not None]
    with_issues = len([
        a for a in per
        if (a.get("success_rate") is not None and a["success_rate"] < 0.95)
        or (a.get("was_correct_null_pct_30d") is not None and a["was_correct_null_pct_30d"] > 0.30)
    ])
    return {
        "last_scan": last,
        "summary": {
            "total_agents_monitored": len(per),
            "agents_with_issues": with_issues,
            "total_calls_24h": sum(a.get("calls_24h") or 0 for a in per),
            "avg_success_rate": round(sum(srs) / len(srs), 3) if srs else None,
        },
    }
