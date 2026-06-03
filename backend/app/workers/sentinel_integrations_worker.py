"""SENTINEL Sprint 2 · Capa 11 (Integraciones externas) cada hora. Module-based. Cierra X4 (monitoreo).

Orquesta los checks de sentinel_integration_checks · scoring por severidad · inserta 1 fila.
coverage_note: liveness = HERMES Capa 1 · MCP/Anthropic = Capa 1/7-A/12 · cero duplicación de ping.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.infrastructure.supabase_service import get_supabase_service
from app.workers.sentinel_integration_checks import check_stripe_webhooks, check_stripe_connect, check_oauth

logger = logging.getLogger(__name__)

PENALTY = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 5}
COVERAGE_NOTE = (
    "Stripe liveness: mcp_health_log (HERMES Capa 1) · Capa 11 NO duplica ping. "
    "OAuth: social_accounts (breakdown por platform) · oauth_tokens (skeleton Meta/Google 00037) sin uso productivo. "
    "Stripe Connect: count from resellers.stripe_account_id · sin status field · live API call skipped (cacheo + costo). "
    "MCP server health: HERMES Capa 1 · Anthropic health: Capa 7-A + Capa 12."
)


async def run_integrations_scan() -> Dict[str, Any]:
    sb = get_supabase_service().client
    webhooks, i1 = check_stripe_webhooks(sb)
    connect, i2 = check_stripe_connect(sb)
    oauth, i3 = check_oauth(sb)
    issues: List[Dict[str, Any]] = i1 + i2 + i3
    score = max(0, 100 - sum(PENALTY.get(i["severity"], 5) for i in issues))
    mcp = {"covered_by": "HERMES Capa 1 (mcp_health_log)", "anthropic_health": "Capa 7-A + Capa 12"}
    scan_id = None
    try:
        ins = sb.table("sentinel_integrations_scans").insert({
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "stripe_webhooks_check": webhooks, "stripe_connect_check": connect,
            "oauth_check": oauth, "mcp_check": mcp, "score": score,
            "issues": issues, "coverage_note": COVERAGE_NOTE,
        }).execute()
        scan_id = (ins.data or [{}])[0].get("id")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"sentinel_integrations_scans insert skip: {e}")
    if score < 80:
        logger.warning(f"SENTINEL integraciones: score {score} · {len(issues)} issues")
    return {"success": True, "score": score, "issues": len(issues), "scan_id": scan_id}
