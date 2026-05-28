"""ARIA Learning Report (DEBT-101) · use case · agrupa agent_memory últimos 7 días por cliente.

Lee `agent_memory` + `training_pairs` (last 7d) + `clients` para name lookup. Retorna métricas
para el formatter del cron lunes 07:05 UTC. Solo incluye clientes con `decisions_total > 0`
(cero ruido). Sin migración: usa schemas existentes (agent_memory · training_pairs · clients).
_aggregate es pure (testeable sin mockear supabase); get_weekly_report orquesta I/O.
"""
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from app.infrastructure.supabase_service import get_supabase_service


def _last_monday_iso() -> str:
    today = datetime.now(timezone.utc).date()
    return (today - timedelta(days=today.weekday())).isoformat()


def _aggregate(mems: list[dict[str, Any]], tps: list[dict[str, Any]],
               name_map: dict[str, str]) -> list[dict[str, Any]]:
    """Pure aggregation · sin I/O · testable directamente."""
    by_client: dict[str, dict[str, Any]] = {}
    for m in mems:
        cid = m.get("client_id")
        if not cid:
            continue
        d = by_client.setdefault(cid, {"total": 0, "correct": 0, "incorrect": 0,
                                       "pending": 0, "agents": Counter()})
        d["total"] += 1
        wc = m.get("was_correct")
        d["correct" if wc is True else "incorrect" if wc is False else "pending"] += 1
        d["agents"][m.get("agent_code") or "unknown"] += 1
    tp_by_client: Counter[str] = Counter(r["client_id"] for r in tps if r.get("client_id"))
    return [{
        "client_id": cid,
        "client_name": name_map.get(cid, "Cliente"),
        "decisions_total": d["total"],
        "correct": d["correct"],
        "incorrect": d["incorrect"],
        "pending": d["pending"],
        "top_agents": [a for a, _ in d["agents"].most_common(3)],
        "training_pairs_generated": tp_by_client.get(cid, 0),
    } for cid, d in by_client.items()]


def get_weekly_report() -> dict[str, Any]:
    """Lee agent_memory + training_pairs últimos 7 días · retorna {week_of, clients[]}."""
    sb = get_supabase_service().client
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    mems = sb.table("agent_memory").select(
        "client_id, agent_code, was_correct").gte("created_at", week_ago).execute().data or []
    tps = sb.table("training_pairs").select(
        "client_id").gte("created_at", week_ago).execute().data or []
    cids = {m["client_id"] for m in mems if m.get("client_id")}
    name_map: dict[str, str] = {}
    if cids:
        rows = sb.table("clients").select("id, name").in_("id", list(cids)).execute().data or []
        name_map = {r["id"]: r["name"] for r in rows}
    return {"week_of": _last_monday_iso(), "clients": _aggregate(mems, tps, name_map)}
