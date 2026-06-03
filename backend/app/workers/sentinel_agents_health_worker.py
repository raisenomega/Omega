"""SENTINEL Capa 12 · salud de agentes IA cada hora. Module-based.

Fuente = ai_provider_calls (agent_log está vacío · hollow). per_agent derivado del USO REAL
(no hardcodea lista). was_correct/accuracy desde agent_memory (LEFT JOIN por agent_code).
Costo = null en V1 (ni agent_log ni ai_provider_calls registran tokens). Coverage_note honesta.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

COVERAGE_NOTE = (
    "Fuente: ai_provider_calls (path canónico) · agent_log vacío (sin instrumentar) · "
    "paths legacy claude_service/AIProviders/nova-chat sin telemetría (DEBT-023/024/025) · "
    "costo no calculable (tokens no registrados V1)."
)


def _memory_stats(sb, agent_code: str, since30: str) -> Dict[str, Any]:
    null_pct, accuracy = None, None
    try:
        total = sb.table("agent_memory").select("id", count="exact").eq("agent_code", agent_code).gte("created_at", since30).execute().count or 0
        if total:
            nulls = sb.table("agent_memory").select("id", count="exact").eq("agent_code", agent_code).is_("was_correct", "null").gte("created_at", since30).execute().count or 0
            null_pct = round(nulls / total, 3)
            evaluated = total - nulls
            if evaluated >= 10:
                correct = sb.table("agent_memory").select("id", count="exact").eq("agent_code", agent_code).eq("was_correct", True).gte("created_at", since30).execute().count or 0
                accuracy = round(correct / evaluated, 3)
    except Exception as e:
        logger.warning(f"agent_memory stats skip {agent_code}: {e}")
    return {"null_pct": null_pct, "accuracy": accuracy}


async def run_agents_health_scan() -> Dict[str, Any]:
    sb = get_supabase_service().client
    now = datetime.now(timezone.utc)
    since24 = (now - timedelta(hours=24)).isoformat()
    since30 = (now - timedelta(days=30)).isoformat()
    try:
        calls = (sb.table("ai_provider_calls").select("agent_code,status,latency_ms,model").gte("created_at", since24).execute().data) or []
    except Exception as e:
        logger.warning(f"ai_provider_calls read skip: {e}")
        calls = []

    by_agent: Dict[str, Dict[str, Any]] = {}
    for c in calls:
        a = c.get("agent_code") or "unknown"
        d = by_agent.setdefault(a, {"calls": 0, "success": 0, "lat": [], "models": {}})
        d["calls"] += 1
        if c.get("status") == "success":
            d["success"] += 1
        if c.get("latency_ms"):
            d["lat"].append(c["latency_ms"])
        if c.get("model"):
            d["models"][c["model"]] = d["models"].get(c["model"], 0) + 1

    per_agent: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    score = 100
    for a, d in by_agent.items():
        total = d["calls"]
        sr = round(d["success"] / total, 3) if total else None
        avg_lat = round(sum(d["lat"]) / len(d["lat"])) if d["lat"] else None
        model_recent = max(d["models"], key=d["models"].get) if d["models"] else None
        mem = _memory_stats(sb, a, since30)
        if sr is not None and sr < 0.95:
            issues.append({"severity": "HIGH", "check": "AGENT_SUCCESS_RATE_LOW", "detail": f"{a}: {sr:.0%} ({total} calls)"})
            score -= 3
        if mem["null_pct"] is not None and mem["null_pct"] > 0.30:
            issues.append({"severity": "MEDIUM", "check": "WAS_CORRECT_LOOP_BROKEN", "detail": f"{a}: {mem['null_pct']:.0%} sin evaluar 30d"})
            score -= 5
        if mem["accuracy"] is not None and mem["accuracy"] < 0.70:
            issues.append({"severity": "HIGH", "check": "AGENT_ACCURACY_LOW", "detail": f"{a} accuracy {mem['accuracy']:.0%}"})
            score -= 5
        per_agent.append({
            "agent_code": a, "calls_24h": total, "success_rate": sr, "avg_latency_ms": avg_lat,
            "was_correct_null_pct_30d": mem["null_pct"], "accuracy_30d": mem["accuracy"], "model_recent": model_recent,
        })

    row = {
        "scanned_at": now.isoformat(),
        "per_agent": per_agent,
        "model_drift_alerts": [],   # skip auto-detección V1 (sin lookup comparativo)
        "total_daily_cost_usd": None,   # tokens no registrados V1
        "cost_calculation_source": None,
        "score": max(score, 0),
        "issues": issues,
        "coverage_note": COVERAGE_NOTE,
    }
    try:
        ins = sb.table("sentinel_agents_health_scans").insert(row).execute()
        scan_id = (ins.data or [{}])[0].get("id")
    except Exception as e:
        logger.warning(f"sentinel_agents_health_scans insert skip: {e}")
        scan_id = None
    if row["score"] < 80:
        logger.warning(f"SENTINEL agents health: score {row['score']} · {len(per_agent)} agentes · {len(issues)} issues")
    return {"success": True, "scan_id": scan_id, "score": row["score"], "agents": len(per_agent)}
