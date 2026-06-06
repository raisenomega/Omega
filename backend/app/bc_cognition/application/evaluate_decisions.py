"""DEBT-100 · evaluate_decisions · cierra was_correct en agent_memory (Loop 1 · P5).

ARIA_LEARNING_LOOP_OMEGA.md §9. Cron horario. La señal de verdad es la decisión
humana sobre el contenido (content_lab_generated.status vía agent_memory.source_event_id):
  · approved/scheduled/published → was_correct = True
  · rejected                     → was_correct = False
  · draft / sin contenido / source_event_id que no apunta a contenido → sin señal aún
A 72h sin señal → evaluated_at = now() · was_correct queda NULL · outcome "Sin señal 72h"
(P1/REGLA 1: jamás se asume un resultado · solo señal real). evaluated_at marca idempotencia.
Fail-safe: cualquier error → log + continúa · nunca rompe el flujo de generación.
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_MIN_AGE_HOURS = 24
_STALE_HOURS = 72
_BATCH = 100
_POSITIVE = ("approved", "scheduled", "published")
_NEGATIVE = ("rejected", "discarded")


async def run_decision_evaluation() -> dict[str, int]:
    """Wrapper async · corre el batch bloqueante en to_thread (no traba el event loop)."""
    return await asyncio.to_thread(_evaluate_pending)


def _evaluate_pending() -> dict[str, int]:
    """Fetch ≤100 decisiones sin evaluar (>24h) → UPDATE was_correct/outcome/evaluated_at."""
    stats = {"evaluated": 0, "correct": 0, "incorrect": 0, "no_signal": 0, "errors": 0}
    sb = get_supabase_service().client
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=_MIN_AGE_HOURS)).isoformat()
    try:
        r = sb.table("agent_memory").select("id, source_event_id, aria_nba_id, created_at") \
            .is_("was_correct", "null").is_("evaluated_at", "null") \
            .lt("created_at", cutoff).order("created_at", desc=False).limit(_BATCH).execute()
    except Exception as e:
        logger.error(f"evaluate_decisions · fetch pendientes failed: {e}", exc_info=True)
        stats["errors"] += 1
        return stats
    for row in (r.data or []):
        try:
            verdict = _decide(sb, row, now)
            if verdict is None:
                continue  # sin señal y <72h → re-evaluar la próxima hora
            sb.table("agent_memory").update(verdict).eq("id", row["id"]).execute()
            if verdict["was_correct"] is True:
                stats["correct"] += 1; stats["evaluated"] += 1
            elif verdict["was_correct"] is False:
                stats["incorrect"] += 1; stats["evaluated"] += 1
            else:
                stats["no_signal"] += 1
        except Exception as e:  # una fila rota no detiene el batch
            stats["errors"] += 1
            logger.error(f"evaluate_decisions · fila {row.get('id')} failed: {e}", exc_info=True)
    logger.info(
        f"evaluate_decisions · evaluadas={stats['evaluated']} correctas={stats['correct']} "
        f"incorrectas={stats['incorrect']} sin_senal={stats['no_signal']} errores={stats['errors']}"
    )
    return stats


def _decide(sb, row: dict, now: datetime) -> Optional[dict]:
    """Dict de UPDATE según la señal · None si todavía no hay señal y no pasaron 72h.

    Punto 0 (loop de verdad): la key del veredicto es `aria_nba_id` = id del content_lab_generated que
    ESTA interacción generó (Commit 2). ANTES se usaba `source_event_id`, que apunta a behavioral_events
    → nunca matcheaba un content_lab_generated → 0 cierres. `source_event_id` SE CONSERVA en la fila
    (sigue siendo el enlace al behavioral), solo deja de ser la key del join. `aria_nba_id` null (Q&A o
    fila vieja · forward-only) → sin contenido → cae al path 72h 'Sin señal' (no rompe, no inventa)."""
    iso = now.isoformat()
    content_id = row.get("aria_nba_id")
    if content_id:
        c = sb.table("content_lab_generated").select("status").eq("id", content_id).limit(1).execute()
        status = c.data[0]["status"] if c.data else None
        if status in _POSITIVE:
            return {"was_correct": True, "outcome": f"Cliente acepto el contenido (status={status})", "evaluated_at": iso}
        if status in _NEGATIVE:
            return {"was_correct": False, "outcome": f"Cliente rechazo el contenido (status={status})", "evaluated_at": iso}
        # status='draft' o content_id sin fila → sin señal aún (fail-open)
    age_h = (now - datetime.fromisoformat(row["created_at"])).total_seconds() / 3600
    if age_h >= _STALE_HOURS:
        return {"was_correct": None, "outcome": "Sin señal 72h", "evaluated_at": iso}
    return None
