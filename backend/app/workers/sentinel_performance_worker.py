"""SENTINEL Capa 10 · scan de performance/APM cada 5 min. Module-based.

CHECK 10.1 p95/p99 por endpoint (rpc sentinel_endpoint_latency) · 10.2 slow queries (rpc) ·
10.3 bundle size (frontend_build_stats) · 10.4 Railway metrics = null (no integrado V1).
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

WINDOW_MIN = 5
P95_LIMIT_MS = 1000        # default · endpoints LLM son legítimamente lentos (no se castiga tan duro)
SLOW_QUERY_MS = 1000
BUNDLE_LIMIT_KB = 800


async def run_performance_scan() -> Dict[str, Any]:
    sb = get_supabase_service().client
    issues: List[Dict[str, Any]] = []
    score = 100

    try:
        endpoints = sb.rpc("sentinel_endpoint_latency", {"window_minutes": WINDOW_MIN}).execute().data or []
    except Exception as e:
        logger.warning(f"endpoint_latency rpc skip: {e}")
        endpoints = []
    for e in endpoints:
        if (e.get("p95") or 0) > P95_LIMIT_MS:
            issues.append({"severity": "MEDIUM", "check": "P95_LATENCY_HIGH",
                           "detail": f"{e['path']} p95={e['p95']}ms (umbral {P95_LIMIT_MS}ms)"})
            score -= 3

    try:
        slow = sb.rpc("sentinel_slow_queries", {"min_mean_ms": SLOW_QUERY_MS, "limit_rows": 5}).execute().data or []
    except Exception as e:
        logger.warning(f"slow_queries rpc skip: {e}")
        slow = []
    for q in slow:
        issues.append({"severity": "MEDIUM", "check": "SLOW_QUERY",
                       "detail": f"mean={q.get('mean_ms')}ms calls={q.get('calls')}: {(q.get('query') or '')[:60]}"})
        score -= 2

    try:
        build = sb.table("frontend_build_stats").select("bundle_size_kb").order("created_at", desc=True).limit(1).execute().data or []
    except Exception:
        build = []
    bundle_kb = build[0]["bundle_size_kb"] if build else None
    if bundle_kb and bundle_kb > BUNDLE_LIMIT_KB:
        issues.append({"severity": "MEDIUM", "check": "BUNDLE_SIZE_EXCEEDED",
                       "detail": f"Bundle {bundle_kb}kb > {BUNDLE_LIMIT_KB}kb"})
        score -= 5

    row = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "window_minutes": WINDOW_MIN,
        "p95_per_endpoint": endpoints,
        "p99_per_endpoint": endpoints,   # mismas filas (cada una trae p95 y p99)
        "slow_queries": slow,
        "bundle_size_kb": bundle_kb,
        "memory_pct": None,   # Railway metrics no integrado V1
        "cpu_pct": None,
        "score": max(score, 0),
        "issues": issues,
    }
    try:
        ins = sb.table("sentinel_performance_scans").insert(row).execute()
        scan_id = (ins.data or [{}])[0].get("id")
    except Exception as e:
        logger.warning(f"sentinel_performance_scans insert skip: {e}")
        scan_id = None
    if row["score"] < 80:
        logger.warning(f"SENTINEL perf: score {row['score']} · {len(endpoints)} endpoints · {len(slow)} slow queries")
    return {"success": True, "scan_id": scan_id, "score": row["score"]}
