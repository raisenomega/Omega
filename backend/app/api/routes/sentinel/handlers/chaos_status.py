"""SENTINEL Capa 8 · estado de chaos engineering para el panel · owner-only."""
from typing import Dict, Any, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin

COVERAGE_NOTE = (
    "Componente 1 (Chaos worker · 5 escenarios controlled in-process/read-only) implementado. "
    "Componente 2 (Pentest profesional externo) ver PENTEST_CHECKLIST_OMEGA.md · DEBT-PENTEST-PROFESSIONAL "
    "· servicio externo $5k-$15k USD semestral. Score 10/10 SENTINEL requiere ese audit (fuera de scope técnico)."
)


async def handle_chaos_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Último scan (filas por escenario que comparten scanned_at) + history 5 recientes."""
    await require_superadmin(authorization)
    sb = get_supabase_service().client
    rows = (sb.table("sentinel_chaos_scans").select("*").order("created_at", desc=True).limit(40).execute().data) or []
    latest_at = rows[0]["scanned_at"] if rows else None
    scenarios = [r for r in rows if r["scanned_at"] == latest_at]
    seen, history = set(), []
    for r in rows:
        if r["scanned_at"] not in seen:
            seen.add(r["scanned_at"])
            history.append({"scanned_at": r["scanned_at"], "score": r["score"]})
        if len(history) >= 5:
            break
    return {
        "last_scanned_at": latest_at,
        "score": scenarios[0]["score"] if scenarios else None,
        "scenarios": scenarios,
        "history": history,
        "coverage_note": COVERAGE_NOTE,
    }
