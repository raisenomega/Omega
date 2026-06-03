"""SENTINEL Capa 8 · escenarios de chaos (controlled + reversibles · in-process / read-only · CERO daño prod).

Cada escenario devuelve dict: {scenario, result, response_observed, expected_response,
recovery_time_ms, graceful_degradation, issues}. El worker orquesta + puntúa + persiste.
"""
import time
from typing import Dict, Any, List


def _r(scenario: str, result: str, observed: Dict[str, Any], expected: Dict[str, Any], rec_ms: int,
       graceful: bool, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {"scenario": scenario, "result": result, "response_observed": observed,
            "expected_response": expected, "recovery_time_ms": rec_ms,
            "graceful_degradation": graceful, "issues": issues}


async def s_anthropic_graceful_failure(sb) -> Dict[str, Any]:
    """generate() con agent_code inválido → ClaudeError sin API call ni excepción (Result-tuple)."""
    from app.bc_cognition.infrastructure.anthropic_adapter import generate
    start = time.monotonic()
    resp, err = await generate("__chaos_invalid_agent__", system="chaos", messages=[{"role": "user", "content": "x"}])
    graceful = resp is None and err is not None
    issues = [] if graceful else [{"severity": "HIGH", "check": "CHAOS_ANTHROPIC", "detail": "adapter no degradó graceful"}]
    return _r("anthropic_graceful_failure", "passed" if graceful else "failed",
              {"raised": False, "error_type": type(err).__name__ if err else None},
              {"raised": False, "returns": "ClaudeError"}, int((time.monotonic() - start) * 1000), graceful, issues)


async def s_db_error_handling(sb) -> Dict[str, Any]:
    """Query a tabla inexistente → error capturable (no crash silencioso del proceso)."""
    start = time.monotonic()
    handled = False
    observed = "no_error"
    try:
        sb.table("__chaos_nonexistent_table__").select("id").limit(1).execute()
    except Exception as e:  # noqa: BLE001 — el error capturable ES el comportamiento esperado
        handled, observed = True, type(e).__name__
    issues = [] if handled else [{"severity": "MEDIUM", "check": "CHAOS_DB", "detail": "query inválida no produjo error capturable"}]
    return _r("db_error_handling", "passed" if handled else "partial",
              {"error_raised": handled, "type": observed}, {"error_raised": True},
              int((time.monotonic() - start) * 1000), handled, issues)


async def s_stripe_idempotency(sb) -> Dict[str, Any]:
    """X4 read-only: ¿webhook_events.event_id tiene UNIQUE? (función de 00059)."""
    start = time.monotonic()
    try:
        enforced = bool(sb.rpc("sentinel_webhook_idempotency_enforced").execute().data)
    except Exception:  # noqa: BLE001
        enforced = False
    issues = [] if enforced else [{"severity": "CRITICAL", "check": "CHAOS_X4", "detail": "event_id sin UNIQUE · idempotencia rota"}]
    return _r("stripe_idempotency", "passed" if enforced else "failed",
              {"idempotency_enforced": enforced}, {"idempotency_enforced": True},
              int((time.monotonic() - start) * 1000), enforced, issues)


async def s_rls_isolation(sb) -> Dict[str, Any]:
    """Lee el último sentinel_rls_audits (Capa 6) · 0 críticos/altos = aislamiento verificado."""
    start = time.monotonic()
    audit = (sb.table("sentinel_rls_audits").select("total_issues,severity_critical,severity_high")
             .order("created_at", desc=True).limit(1).execute().data or [None])[0]
    if not audit:
        return _r("rls_isolation", "skipped", {"reason": "sin auditoría RLS (Capa 6) aún"}, {"crit_high": 0}, 0, True, [])
    crit_high = (audit.get("severity_critical") or 0) + (audit.get("severity_high") or 0)
    issues = [] if crit_high == 0 else [{"severity": "HIGH", "check": "CHAOS_RLS", "detail": f"{crit_high} gaps RLS crit/high (Capa 6)"}]
    return _r("rls_isolation", "passed" if crit_high == 0 else "failed",
              {"crit_high_gaps": crit_high}, {"crit_high_gaps": 0}, int((time.monotonic() - start) * 1000), crit_high == 0, issues)


async def s_rate_limit_effective(sb) -> Dict[str, Any]:
    """Instancia RateLimitMiddleware in-process → limit+1 requests misma IP debe dar 429 (cero red)."""
    from starlette.requests import Request
    from starlette.responses import Response
    from app.api.rate_limit_middleware import RateLimitMiddleware
    start = time.monotonic()
    mw = RateLimitMiddleware(app=None, limit_per_minute=5)

    async def _call_next(_req):
        return Response("ok")

    blocked = False
    for _ in range(7):  # límite 5 → la 6ª debe bloquear
        scope = {"type": "http", "method": "GET", "path": "/api/v1/__chaos_probe__",
                 "headers": [(b"x-forwarded-for", b"203.0.113.99")], "client": ("203.0.113.99", 0)}
        resp = await mw.dispatch(Request(scope), _call_next)
        if resp.status_code == 429:
            blocked = True
            break
    issues = [] if blocked else [{"severity": "HIGH", "check": "CHAOS_RATE_LIMIT", "detail": "middleware no bloqueó en limit+1"}]
    return _r("rate_limit_effective", "passed" if blocked else "failed",
              {"blocked_at_limit_plus_1": blocked}, {"blocked_at_limit_plus_1": True},
              int((time.monotonic() - start) * 1000), blocked, issues)
