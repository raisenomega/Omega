"""Handler: estado de los AI providers (Anthropic/Bedrock/Vertex) + cobertura honesta · owner-only."""
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.bc_cognition.infrastructure.ai_provider_router import get_ai_provider_router

# Paths legacy que NO pasan por el router (DEBT-023/024/025 · ver diagnóstico Capa 7).
_LEGACY_UNCOVERED = [
    {"name": "claude_service", "debt": "DEBT-023/024", "callers_count": 10},
    {"name": "AIProviders (services/ai_providers.py)", "debt": "DEBT-025", "callers_count": 1},
    {"name": "nova-chat raw httpx", "debt": "pending_doc", "callers_count": 1},
]


async def handle_ai_providers_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Por provider: configured, circuit, stats 24h. + coverage honesta (% unknown en V1)."""
    await require_superadmin(authorization)
    router = get_ai_provider_router()
    sb = get_supabase_service().client
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    try:
        rows = (sb.table("ai_provider_calls").select("provider,status,latency_ms")
                .gte("created_at", since).execute().data) or []
    except Exception:
        rows = []

    now = time.monotonic()
    providers: List[Dict[str, Any]] = []
    for p in router.providers:
        pr = [r for r in rows if r["provider"] == p.name]
        success = [r for r in pr if r["status"] == "success"]
        failed = [r for r in pr if r["status"] == "failed"]
        failover = [r for r in pr if r["status"] == "failover_triggered"]
        lat = [r["latency_ms"] for r in success if r.get("latency_ms")]
        total = len(success) + len(failed)
        providers.append({
            "name": p.name,
            "configured": p.configured,
            "reason_not_configured": p.reason_not_configured,
            "circuit_state": "open" if router.circuit_open(p.name, now) else "closed",
            "consecutive_failures": router._fails.get(p.name, 0),
            "last_24h": {
                "total_calls": total, "success": len(success), "failed": len(failed),
                "success_rate": round(len(success) / total, 3) if total else None,
                "avg_latency_ms": round(sum(lat) / len(lat)) if lat else None,
                "failover_triggered_count": len(failover),
            },
        })

    return {
        "providers": providers,
        "coverage_summary": {
            "canonical_path_covered": True,
            "legacy_paths_uncovered": _LEGACY_UNCOVERED,
        },
        "pct_calls_covered_by_router": None,
        "coverage_percentage_unknown": True,
        "total_router_calls_24h": len([r for r in rows if r["status"] in ("success", "failed")]),
    }
