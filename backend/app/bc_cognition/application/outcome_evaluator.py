"""Cron outcome_evaluator · PASO 3 del ciclo de auto-aprendizaje (4A-2 · P5).

Registra el outcome NEGATIVO de drafts abandonados: contenido generado que a las
72h sigue en status='draft' (nunca aprobado/guardado) → agent_memory.was_correct=False.
Proxy is_saved=status (sin Meta API · spec OMEGA_AGENT_SYSTEM "CICLO AUTO-APRENDIZAJE").
El positivo (aprobado→was_correct=True) ya lo registra insert_agent_memory_approved.
Idempotente vía content_lab_generated.outcome_evaluated_at (migración 00026).
"""
import logging
from datetime import datetime, timedelta, timezone
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.domain.input_threats import redact_pii

logger = logging.getLogger(__name__)

_WINDOW_HOURS = 72
_BATCH = 200


async def run_outcome_evaluation() -> dict[str, object]:
    """Drafts >72h sin guardar → was_correct=False en agent_memory. Best-effort por fila.
    Retorna {evaluated, failed, errors} · errors capado a 25 (diagnóstico endpoint + log)."""
    sb = get_supabase_service().client
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=_WINDOW_HOURS)).isoformat()
    errors: list[str] = []
    try:
        r = sb.table("content_lab_generated").select("id, client_id, agent_code, prompt") \
            .eq("status", "draft").is_("outcome_evaluated_at", "null") \
            .lte("created_at", cutoff).limit(_BATCH).execute()
    except Exception as e:
        logger.error(f"outcome_evaluator · fetch drafts failed: {e}", exc_info=True)
        return {"evaluated": 0, "failed": 0, "errors": [f"fetch: {e}"]}

    now = datetime.now(timezone.utc).isoformat()
    evaluated = 0
    failed = 0
    for row in (r.data or []):
        try:
            _record_negative(sb, row, now)
            evaluated += 1
        except Exception as e:  # una fila rota no detiene el batch
            failed += 1
            if len(errors) < 25:
                errors.append(f"row {row.get('id')}: {e}")
            logger.error(f"outcome_evaluator · row {row.get('id')} failed: {e}", exc_info=True)
    logger.info(f"outcome_evaluator · evaluated={evaluated} failed={failed} (drafts abandonados 72h)")
    return {"evaluated": evaluated, "failed": failed, "errors": errors}


def _record_negative(sb, row: dict, now: str) -> None:
    """1 fila: INSERT agent_memory(was_correct=False) → marca outcome_evaluated_at (idempotencia).
    INSERT primero (la señal de aprendizaje es lo importante); marca después. Un fallo entre
    ambos solo arriesga 1 duplicado en el próximo run (raro · preferible a perder la señal)."""
    sb.table("agent_memory").insert({
        "client_id": row.get("client_id"),
        "agent_code": row.get("agent_code") or "content_creator",
        "memory_type": "procedural",
        "context": redact_pii(row.get("prompt") or "")[0][:500],
        "decision": "generated_not_saved",
        "outcome": "draft_abandoned_72h",
        "was_correct": False,
        "confidence": 5,
        "metadata": {"content_id": str(row["id"]), "proxy": "status_is_saved"},
        "evaluated_at": now,
    }).execute()
    sb.table("content_lab_generated").update({"outcome_evaluated_at": now}).eq("id", row["id"]).execute()
