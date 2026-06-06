"""ESLABÓN 3 · DEBT-ARIA-NOVA-BRIDGE · fachada de lectura: compone los lectores existentes del
stream de ARIA para que NOVA parta de lo que ARIA vivió. fetch_recent_for_owner (interacciones por
cliente) + _aggregate (conteos por negocio). CONTEOS HONESTOS · NUNCA accuracy % (P1): was_correct
sin señal de calidad hoy. with_real_verdict = True/False que NO sea fallo de API.
DDD A1 (application · sin anthropic/fastapi). Fail-safe: lector que falla → estructura vacía honesta."""
import logging
from typing import Optional

from app.bc_cognition.infrastructure.aria_memory_repository import (
    fetch_recent_for_owner, _ARIA_AGENT_CODES,
)
from app.bc_cognition.application.aria_learning_report import _aggregate

logger = logging.getLogger(__name__)

_SNIPPET = 150
_COUNT_WINDOW = 200        # filas leídas para contar (las 88 de un negocio entran holgadas)
_API_FAIL_PREFIX = "[failed:"


def _snip(value: object, n: int = _SNIPPET) -> str:
    """Trunca a ≤n chars (+ elipsis). No-string → ''."""
    if not isinstance(value, str):
        return ""
    value = value.strip()
    return (value[:n] + "…") if len(value) > n else value


def _is_real_verdict(row: dict) -> bool:
    """Veredicto de CALIDAD real: was_correct True/False que NO sea fallo de API
    (`[failed:...]` con was_correct=False es error técnico, no juicio de calidad)."""
    if row.get("was_correct") not in (True, False):
        return False
    return not (row.get("decision") or "").startswith(_API_FAIL_PREFIX)


def _honest_counts(rows: list[dict]) -> dict[str, int]:
    """total · with_real_verdict (veredictos de calidad reales) · no_signal (resto). Cero %."""
    real = sum(1 for r in rows if _is_real_verdict(r))
    return {"total": len(rows), "with_real_verdict": real, "no_signal": len(rows) - real}


def aria_learning_for_client(supabase, client_id: Optional[str], limit: int = 8) -> dict:
    """Lo que ARIA vivió con UN negocio: últimas `limit` interacciones + conteos honestos (lee
    ≤_COUNT_WINDOW para contar, recorta a `limit` para snippets). Reusa fetch_recent_for_owner."""
    empty = {"client_id": client_id, "interactions": [],
             "counts": {"total": 0, "with_real_verdict": 0, "no_signal": 0}}
    if not client_id:
        return empty
    try:
        rows = fetch_recent_for_owner(supabase, client_id=client_id, limit=_COUNT_WINDOW)
    except Exception as e:
        logger.error(f"aria_learning_for_client({client_id}) failed: {e}", exc_info=True)
        return empty
    interactions = [{
        "context_snippet": _snip(r.get("context")), "decision_snippet": _snip(r.get("decision")),
        "was_correct": r.get("was_correct"), "created_at": r.get("created_at"),
    } for r in rows[:limit]]
    return {"client_id": client_id, "interactions": interactions, "counts": _honest_counts(rows)}


def aria_learning_global(supabase) -> dict:
    """Panorama de la cartera: por negocio, conteos honestos del stream ARIA (all-time).
    Reusa _aggregate (pure) + refina with_real_verdict decision-aware. Fail-safe → vacío."""
    empty = {"businesses": [], "grand_total": 0}
    try:
        sb = supabase.client
        # Lectura all-time global de agent_code=aria: la data real es >7d, la ventana 7d de
        # get_weekly_report saldría vacía. NO duplica lector existente (ninguno hace all-time-global).
        # Patrón: application leyendo agent_memory, igual que aria_learning_report.py.
        mems = sb.table("agent_memory").select(
            "client_id, agent_code, was_correct, decision"
        ).in_("agent_code", list(_ARIA_AGENT_CODES)).execute().data or []
    except Exception as e:
        logger.error(f"aria_learning_global read failed: {e}", exc_info=True)
        return empty
    if not mems:
        return empty
    name_map: dict[str, str] = {}
    cids = [c for c in {m.get("client_id") for m in mems} if c]
    try:
        rows = sb.table("clients").select("id, name").in_("id", cids).execute().data or []
        name_map = {r["id"]: r["name"] for r in rows}
    except Exception as e:
        logger.warning(f"aria_learning_global name_map best-effort failed: {e}")
    real: dict[str, int] = {}
    for m in mems:
        cid = m.get("client_id")
        if cid:
            real[cid] = real.get(cid, 0) + (1 if _is_real_verdict(m) else 0)
    businesses = [{
        "client_id": a["client_id"], "name": a.get("client_name"), "total": a["decisions_total"],
        "with_real_verdict": real.get(a["client_id"], 0),
        "no_signal": a["decisions_total"] - real.get(a["client_id"], 0),
    } for a in _aggregate(mems, [], name_map)]
    businesses.sort(key=lambda b: b["total"], reverse=True)
    return {"businesses": businesses, "grand_total": sum(b["total"] for b in businesses)}
