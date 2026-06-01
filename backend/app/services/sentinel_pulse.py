"""
SENTINEL PULSE MONITOR — Endpoint Health & Auth Regression
Verifica disponibilidad, latencia y que los endpoints protegidos
requieran autenticación.
MAX 200L — R-LINES-001
"""
import os
import time
import logging
from typing import Dict, Any

from app.services.sentinel_helpers import _calculate_score, _get_status

logger = logging.getLogger(__name__)

# ── CONFIG ────────────────────────────────────────────────────

# SENTINEL_SELF_URL override opcional (Railway) · fallback = URL real de prod (3c67). Si el dominio
# cambia, se setea la env var sin re-deploy de código; si no está, cae a la URL correcta actual,
# NUNCA a una vieja. Antes hardcodeaba "...2031..." (fantasma) → pulse_monitor reportaba todo
# unreachable y arrastraba el score SENTINEL con CRITICAL falsos.
_ROOT_URL = os.environ.get("SENTINEL_SELF_URL", "https://omega-production-3c67.up.railway.app").rstrip("/")

# (path, method, expected_status, requires_auth)
# requires_auth=True → un 200 sin token es CRITICAL AUTH_REGRESSION
ENDPOINTS = [
    ("/health",              "GET",  200, False),
    ("/api/v1/omega/agents/", "GET",  200, False),
    ("/api/v1/clients/",     "GET",  401, True),
    ("/api/v1/nova/chat/",   "POST", 422, True),
]

SLOW_THRESHOLD_MS = 3000


# ── SCAN ──────────────────────────────────────────────────────

async def run_pulse_monitor() -> Dict[str, Any]:
    """
    Health check + auth regression de endpoints críticos.

    Checks por endpoint:
      5xx             → CRITICAL ENDPOINT_DOWN
      auth_bypass     → CRITICAL AUTH_REGRESSION
      wrong_status    → HIGH    UNEXPECTED_STATUS
      latency > 2s    → HIGH    SLOW_ENDPOINT
      unreachable     → CRITICAL ENDPOINT_UNREACHABLE
    """
    scan_start = time.time()
    import httpx
    results, issues = [], []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for path, method, expected_code, requires_auth in ENDPOINTS:
                start = time.time()
                try:
                    if method == "POST":
                        r = await client.post(f"{_ROOT_URL}{path}", json={})
                    else:
                        r = await client.get(f"{_ROOT_URL}{path}")

                    latency = (time.time() - start) * 1000
                    status = "pass"

                    if r.status_code >= 500:
                        status = "critical"
                        issues.append({
                            "severity": "CRITICAL",
                            "type": "ENDPOINT_DOWN",
                            "message": f"{path} → {r.status_code}",
                        })
                    elif requires_auth and r.status_code == 200:
                        status = "critical"
                        issues.append({
                            "severity": "CRITICAL",
                            "type": "AUTH_REGRESSION",
                            "message": f"{path} retorna 200 sin token — auth removida",
                        })
                    elif r.status_code != expected_code and r.status_code < 500:
                        status = "warning"
                        issues.append({
                            "severity": "HIGH",
                            "type": "UNEXPECTED_STATUS",
                            "message": f"{path} → {r.status_code} (esperado {expected_code})",
                        })
                    elif latency > SLOW_THRESHOLD_MS:
                        status = "warning"
                        issues.append({
                            "severity": "HIGH",
                            "type": "SLOW_ENDPOINT",
                            "message": f"{path} → {latency:.0f}ms",
                        })

                    results.append({
                        "endpoint": path,
                        "method": method,
                        "status_code": r.status_code,
                        "latency_ms": round(latency),
                        "health": status,
                    })

                except Exception as e:
                    issues.append({
                        "severity": "CRITICAL",
                        "type": "ENDPOINT_UNREACHABLE",
                        "message": f"{path}: {str(e)[:80]}",
                    })

    except Exception as e:
        logger.error(f"Pulse error: {e}")

    score = _calculate_score(issues)
    return {
        "agent_code": "PULSE_MONITOR",
        "scan_type": "performance",
        "status": _get_status(score),
        "security_score": score,
        "issues": issues,
        "details": results,
        "scan_duration_ms": int((time.time() - scan_start) * 1000),
        "deploy_decision": "BLOCK" if score < 70 else "APPROVE",
    }
