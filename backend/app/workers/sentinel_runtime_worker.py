"""SENTINEL Capa 9 · scan de observabilidad runtime cada 5 min. Module-based (decision_evaluator).

CHECK 9.2 lee backend_error_log (no omega_audit_log · fantasma). CHECK 9.1 error_rate% = null
hasta request_timing_log (Capa 10). CHECK 9.5 Railway logs no integrado en V1 (null).
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

WINDOW_MIN = 5
RECURRING_THRESHOLD = 5


async def run_runtime_observability_scan() -> Dict[str, Any]:
    """Calcula errores backend/frontend + patrones recurrentes en la ventana · persiste."""
    sb = get_supabase_service().client
    since = (datetime.now(timezone.utc) - timedelta(minutes=WINDOW_MIN)).isoformat()
    issues: List[Dict[str, Any]] = []
    score = 100

    try:
        be = (sb.table("backend_error_log").select("error_class").gte("created_at", since).execute().data) or []
        fe = (sb.table("frontend_error_log").select("signature,message").gte("created_at", since).execute().data) or []
    except Exception as e:
        logger.warning(f"runtime scan read skip: {e}")
        be, fe = [], []

    # CHECK 9.1 · error_rate desde request_timing_log (Capa 10 cerró el loop) · null si sin tráfico.
    error_rate = None
    try:
        total = sb.table("request_timing_log").select("id", count="exact").gte("created_at", since).execute().count or 0
        if total > 0:
            errs = (sb.table("request_timing_log").select("id", count="exact")
                    .gte("created_at", since).gte("status_code", 500).execute().count) or 0
            error_rate = round(errs / total * 100, 2)
            if error_rate > 1.0:
                issues.append({"severity": "HIGH", "check": "BACKEND_ERROR_RATE",
                               "detail": f"error_rate {error_rate}% (de {total} requests en {WINDOW_MIN}min)"})
                score -= 10
    except Exception as e:
        logger.warning(f"error_rate calc skip: {e}")

    backend_count, frontend_count = len(be), len(fe)
    if backend_count > 10:
        issues.append({"severity": "HIGH", "check": "BACKEND_ERRORS_SPIKE",
                       "detail": f"{backend_count} errores backend en {WINDOW_MIN}min"})
        score -= 10
    if frontend_count > 20:
        issues.append({"severity": "MEDIUM", "check": "FRONTEND_ERRORS_SPIKE",
                       "detail": f"{frontend_count} errores frontend en {WINDOW_MIN}min"})
        score -= 5

    # CHECK 9.4 · patrones recurrentes (>=5 mismo signature/error_class)
    counts: Dict[str, Dict[str, Any]] = {}
    for r in fe:
        sig = r.get("signature") or "?"
        c = counts.setdefault(f"fe:{sig}", {"source": "frontend", "sample": (r.get("message") or "")[:120], "count": 0})
        c["count"] += 1
    for r in be:
        k = r.get("error_class") or "?"
        c = counts.setdefault(f"be:{k}", {"source": "backend", "sample": k, "count": 0})
        c["count"] += 1
    recurring = []
    for c in counts.values():
        if c["count"] >= RECURRING_THRESHOLD:
            recurring.append(c)
            issues.append({"severity": "MEDIUM", "check": "RECURRING_ERROR_PATTERN",
                           "detail": f"{c['source']} '{c['sample']}' x{c['count']}"})
            score -= 3

    row = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "window_minutes": WINDOW_MIN,
        "backend_error_rate_pct": error_rate,    # Capa 10 cerró el loop (null si sin tráfico)
        "backend_exception_count": backend_count,
        "frontend_error_count": frontend_count,
        "recurring_patterns": recurring,
        "railway_5xx_count": None,         # Railway logs no integrado en V1
        "score": max(score, 0),
        "issues": issues,
    }
    try:
        ins = sb.table("sentinel_runtime_scans").insert(row).execute()
        scan_id = (ins.data or [{}])[0].get("id")
    except Exception as e:
        logger.warning(f"sentinel_runtime_scans insert skip: {e}")
        scan_id = None
    if row["score"] < 80:
        logger.warning(f"SENTINEL runtime: score {row['score']} · {backend_count} backend / {frontend_count} frontend")
    return {"success": True, "scan_id": scan_id, "score": row["score"]}
