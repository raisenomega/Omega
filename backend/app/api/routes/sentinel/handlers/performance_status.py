"""SENTINEL Capa 10 · estado de performance/APM para el panel · owner-only."""
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin


async def handle_performance_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan + top endpoints lentos 24h + tendencia de bundle."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    last = (sb.table("sentinel_performance_scans").select("*")
            .order("created_at", desc=True).limit(1).execute().data or [None])[0]
    try:
        top = sb.rpc("sentinel_endpoint_latency", {"window_minutes": 1440}).execute().data or []
    except Exception:
        top = []
    builds = (sb.table("frontend_build_stats").select("git_sha,bundle_size_kb,created_at")
              .order("created_at", desc=True).limit(5).execute().data) or []

    last_build_age_hours: Optional[float] = None
    if builds:
        try:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(builds[0]["created_at"])
            last_build_age_hours = round(age.total_seconds() / 3600, 1)
        except Exception:
            last_build_age_hours = None

    return {
        "last_scan": last,
        "last_24h": {
            "top_5_slowest_endpoints_p95": top[:5],
            "bundle_size_trend": builds,
        },
        "coverage": {
            "pg_stat_statements_enabled": True,
            "railway_metrics_active": False,
            "last_build_age_hours": last_build_age_hours,
        },
    }
