"""SENTINEL Capa 11 · checks de integraciones (Stripe webhooks/Connect · OAuth). Aislados del worker (C4).

Cada check devuelve (data: dict, issues: list). Lee SOLO de la DB (P1 · sin calls live a Stripe/Meta).
"""
import logging
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def _min_expiry(row: Dict[str, Any]):
    vals = [v for v in (row.get("token_expires_at"), row.get("expires_at")) if v]
    return min(vals) if vals else None


def check_stripe_webhooks(sb) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """event_count_24h + X4 estructural (RPC) + liveness desde mcp_health_log (HERMES · no re-pinguea)."""
    issues: List[Dict[str, Any]] = []
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    count = sb.table("webhook_events").select("id", count="exact").gte("processed_at", since).execute().count or 0
    try:
        enforced = bool(sb.rpc("sentinel_webhook_idempotency_enforced").execute().data)
    except Exception as e:  # noqa: BLE001
        logger.warning(f"X4 rpc skip: {e}"); enforced = None
    if enforced is False:
        issues.append({"severity": "CRITICAL", "check": "X4_IDEMPOTENCY_BROKEN",
                       "detail": "webhook_events.event_id sin UNIQUE · idempotencia Stripe rota"})
    live = (sb.table("mcp_health_log").select("status,checked_at").eq("integration", "stripe")
            .order("checked_at", desc=True).limit(1).execute().data or [None])[0]
    liveness = live["status"] if live else None
    if liveness and liveness != "ok":
        issues.append({"severity": "HIGH", "check": "STRIPE_LIVENESS", "detail": f"HERMES reporta stripe={liveness}"})
    return ({"event_count_24h": count, "idempotency_enforced": enforced, "stripe_liveness": liveness,
             "liveness_checked_at": live["checked_at"] if live else None,
             "liveness_note": None if live else "HERMES sin ping Stripe en ventana"}, issues)


def check_stripe_connect(sb) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Count resellers con stripe_account_id (sin status/payout · sin call live)."""
    rows = sb.table("resellers").select("stripe_account_id").execute().data or []
    with_acct = sum(1 for r in rows if r.get("stripe_account_id"))
    return ({"total_resellers": len(rows), "with_stripe_account": with_acct,
             "note": "sin status/payout field en resellers · live Stripe API skipped (cacheo + costo)"}, [])


def check_oauth(sb) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """social_accounts por platform + tokens venciendo (<24h CRITICAL · <7d HIGH)."""
    issues: List[Dict[str, Any]] = []
    rows = sb.table("social_accounts").select(
        "platform,oauth_status,status,token_expires_at,expires_at").execute().data or []
    now = datetime.now(timezone.utc)
    per: Dict[str, Dict[str, int]] = defaultdict(lambda: {"count": 0, "connected": 0, "expiring_24h": 0, "expiring_7d": 0})
    exp24 = exp7 = 0
    for r in rows:
        p = per[r.get("platform") or "unknown"]
        p["count"] += 1
        if r.get("oauth_status") == "connected":
            p["connected"] += 1
        exp = _min_expiry(r)
        if not exp:
            continue
        try:
            dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            continue
        hrs = (dt - now).total_seconds() / 3600
        if hrs <= 24:
            p["expiring_24h"] += 1; exp24 += 1
        elif hrs <= 168:
            p["expiring_7d"] += 1; exp7 += 1
    if exp24:
        issues.append({"severity": "CRITICAL", "check": "OAUTH_TOKEN_EXPIRING", "detail": f"{exp24} token(s) OAuth vencen en <24h"})
    if exp7:
        issues.append({"severity": "HIGH", "check": "OAUTH_TOKEN_EXPIRING", "detail": f"{exp7} token(s) OAuth vencen en <7d"})
    return ({"total": len(rows), "expiring_24h": exp24, "expiring_7d": exp7,
             "per_platform": [{"platform": k, **v} for k, v in per.items()]}, issues)
