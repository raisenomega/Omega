"""SENTINEL Sprint 2 · Capa 3 (Red y HTTP) cada 2h. Module-based.

CHECK 3.1 security headers · 3.2 TLS (cert + expiry) · 3.3 rate-limit (introspección de config ·
ráfaga sintética = DEBT-RATE-LIMIT-SYNTHETIC-TEST · el worker corre EN Railway, martillar auto-bloquea) ·
3.4 CORS (origen no confiable no debe reflejarse). Inserta 1 fila por target.
Targets: www.omegaraisen.agency (frontend) + Railway /health (backend).
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from urllib.parse import urlparse

from app.infrastructure.supabase_service import get_supabase_service
from app.config import settings
from app.api.rate_limit_middleware import _EXEMPT_PREFIXES
from app.workers.sentinel_network_checks import check_headers, check_tls, check_cors

logger = logging.getLogger(__name__)

FRONTEND = "https://www.omegaraisen.agency"
BACKEND = "https://omega-production-3c67.up.railway.app"


def _rate_limit_config() -> Dict[str, Any]:
    return {
        "active": settings.rate_limit_per_minute > 0,
        "limit_per_minute": settings.rate_limit_per_minute,
        "scope": "in-memory single-instance",
        "exempt_prefixes": list(_EXEMPT_PREFIXES),
        "verified_by": "config_introspection",
    }


async def _scan_target(url: str, is_backend: bool) -> Dict[str, Any]:
    host = urlparse(url).netloc
    issues: List[Dict[str, Any]] = []
    score = 100

    headers = await check_headers(url + ("/health" if is_backend else ""), want_csp=not is_backend)
    for m in headers["missing"]:
        sev = "MEDIUM" if m == "Content-Security-Policy" else "HIGH"
        issues.append({"severity": sev, "check": "HEADER_MISSING", "detail": f"{host}: falta {m}"})
        score -= 3

    tls = await check_tls(host)
    days = tls.get("days_until_expiry")
    if "error" in tls:
        issues.append({"severity": "HIGH", "check": "TLS_ERROR", "detail": f"{host}: {tls['error']}"}); score -= 20
    elif days is not None and days < 7:
        issues.append({"severity": "CRITICAL", "check": "TLS_EXPIRING", "detail": f"{host}: cert vence en {days}d"}); score -= 50
    elif days is not None and days < 30:
        issues.append({"severity": "HIGH", "check": "TLS_EXPIRING", "detail": f"{host}: cert vence en {days}d"}); score -= 10

    rate = _rate_limit_config() if is_backend else None
    cors = await check_cors(url) if is_backend else None
    if cors and (cors.get("wildcard_detected") or cors.get("reflects_untrusted")):
        issues.append({"severity": "HIGH", "check": "CORS_WEAK", "detail": f"{host}: CORS refleja origen no confiable"}); score -= 15

    return {"target_url": url, "headers_check": headers, "tls_check": tls,
            "rate_limit_check": rate, "cors_check": cors, "score": max(score, 0), "issues": issues}


async def run_network_http_scan() -> Dict[str, Any]:
    sb = get_supabase_service().client
    results = [await _scan_target(FRONTEND, False), await _scan_target(BACKEND, True)]
    total_issues = sum(len(r["issues"]) for r in results)
    overall = round(sum(r["score"] for r in results) / len(results))
    last_id = None
    for r in results:
        try:
            ins = sb.table("sentinel_network_http_scans").insert({
                "scanned_at": datetime.now(timezone.utc).isoformat(), "target_url": r["target_url"],
                "headers_check": r["headers_check"], "tls_check": r["tls_check"],
                "rate_limit_check": r["rate_limit_check"], "cors_check": r["cors_check"],
                "score": r["score"], "issues": r["issues"],
            }).execute()
            last_id = (ins.data or [{}])[0].get("id")
        except Exception as e:  # noqa: BLE001
            logger.warning(f"sentinel_network_http_scans insert skip: {e}")
    if overall < 80:
        logger.warning(f"SENTINEL net/http: overall {overall} · {total_issues} issues")
    return {"success": True, "overall_score": overall, "issues": total_issues, "scan_id": last_id}
