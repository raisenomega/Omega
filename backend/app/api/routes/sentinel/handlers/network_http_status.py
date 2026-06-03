"""SENTINEL Capa 3 · estado Red/HTTP para el panel · owner-only."""
from typing import Dict, Any, Optional, List

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin

TARGETS = ["https://www.omegaraisen.agency", "https://omega-production-3c67.up.railway.app"]
COVERAGE_NOTE = "El header Server lo fija el proxy de Railway (railway-hikari) · no stripeable desde FastAPI · no es issue."


async def handle_network_http_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan por target + promedio 24h + score global."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    targets: List[Dict[str, Any]] = []
    scores: List[int] = []
    for url in TARGETS:
        rows = (sb.table("sentinel_network_http_scans").select("*")
                .eq("target_url", url).order("created_at", desc=True).limit(12).execute().data) or []
        last = rows[0] if rows else None
        if last:
            scores.append(last["score"])
        targets.append({
            "url": url,
            "last_scan": last,
            "last_24h_avg_score": round(sum(r["score"] for r in rows) / len(rows)) if rows else None,
        })
    return {
        "targets": targets,
        "overall_score": round(sum(scores) / len(scores)) if scores else None,
        "coverage_note": COVERAGE_NOTE,
    }
