"""SENTINEL Sprint 2 · Capa 8 mínima (Chaos Engineering) · 1er lunes/mes 3AM + on-demand. Module-based.

Componente 1 (chaos worker · 5 escenarios controlled) implementado aquí. Componente 2 (pentest
profesional externo) = PENTEST_CHECKLIST_OMEGA.md + DEBT-PENTEST-PROFESSIONAL. Inserta 1 fila por escenario.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.workers.sentinel_chaos_scenarios import (
    s_anthropic_graceful_failure, s_db_error_handling, s_stripe_idempotency,
    s_rls_isolation, s_rate_limit_effective, _r,
)

logger = logging.getLogger(__name__)

SCENARIOS = {
    "anthropic_graceful_failure": s_anthropic_graceful_failure,
    "db_error_handling": s_db_error_handling,
    "stripe_idempotency": s_stripe_idempotency,
    "rls_isolation": s_rls_isolation,
    "rate_limit_effective": s_rate_limit_effective,
}
PENALTY = {"partial": 10, "failed": 25, "skipped": 5}


async def run_chaos_scan(scenarios: Optional[List[str]] = None, trigger_source: str = "cron") -> Dict[str, Any]:
    sb = get_supabase_service().client
    names = [n for n in (scenarios or list(SCENARIOS)) if n in SCENARIOS]
    results: List[Dict[str, Any]] = []
    for n in names:
        try:
            results.append(await SCENARIOS[n](sb))
        except Exception as e:  # noqa: BLE001 — un escenario que crashea = failed (no tumba el scan)
            results.append(_r(n, "failed", {"exception": str(e)[:100]}, {}, 0, False,
                              [{"severity": "HIGH", "check": "CHAOS_CRASH", "detail": str(e)[:100]}]))
    score = max(0, 100 - sum(PENALTY.get(r["result"], 0) for r in results))
    scanned_at = datetime.now(timezone.utc).isoformat()
    for r in results:
        try:
            sb.table("sentinel_chaos_scans").insert({
                "scanned_at": scanned_at, "scenario": r["scenario"], "result": r["result"],
                "response_observed": r["response_observed"], "expected_response": r["expected_response"],
                "recovery_time_ms": r["recovery_time_ms"], "graceful_degradation": r["graceful_degradation"],
                "score": score, "issues": r["issues"], "trigger_source": trigger_source,
            }).execute()
        except Exception as e:  # noqa: BLE001
            logger.warning(f"sentinel_chaos_scans insert skip: {e}")
    if score < 80:
        logger.warning(f"SENTINEL chaos: score {score} · {[r['scenario'] for r in results if r['result'] != 'passed']}")
    return {"success": True, "score": score, "scenarios": len(results),
            "results": [{"scenario": r["scenario"], "result": r["result"], "recovery_ms": r["recovery_time_ms"]} for r in results]}
