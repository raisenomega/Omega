"""Repository ARIA memory · agent_memory inserts + reads + delete history.

Separado de aria_repository (DDD A1/A9 · C4 split a ≤75L).
T4 Sprint 1: fetch_recent_for_owner agregado para inyectar memoria al system.
"""
import logging
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService
from app.bc_cognition.domain.input_threats import redact_pii

logger = logging.getLogger(__name__)

_ARIA_AGENT_CODES = ("aria", "aria_1", "aria_2", "aria_3", "aria_4")


def insert_agent_memory(
    supabase: SupabaseService, user_id: str,
    client_id: Optional[str], reseller_id: Optional[str],
    user_message: str, assistant_response: str, level: int,
    source_event_id: Optional[str], was_correct: Optional[bool] = None,
) -> None:
    """INSERT agent_memory schema M1 · was_correct=None → cron evalúa 72h."""
    supabase.client.table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "reseller_id": reseller_id,
        "agent_code": "aria", "memory_type": "episodic",
        "context": redact_pii(user_message)[0], "decision": redact_pii(assistant_response)[0], "confidence": 7,
        "was_correct": was_correct, "source_event_id": source_event_id,
        "metadata": {"aria_level": level},
    }).execute()


def delete_aria_history(supabase: SupabaseService, user_id: str) -> None:
    """DELETE aria_conversations WHERE user_id · Settings ARIA tab."""
    supabase.client.table("aria_conversations").delete().eq("user_id", user_id).execute()


def fetch_recent_for_owner(
    supabase: SupabaseService, client_id: Optional[str] = None,
    reseller_id: Optional[str] = None, limit: int = 10,
) -> list[dict]:
    """Últimas `limit` filas ARIA en agent_memory para client_id o reseller_id.

    Filtro: agent_code IN aria/aria_1..4 AND owner match. Best-effort:
    si Supabase falla → log + [] (no romper la conversación · P5 mejor débil
    que crash). Llamado desde application._aria_memory_context.
    """
    if not (client_id or reseller_id):
        return []
    try:
        q = supabase.client.table("agent_memory").select(
            "id, context, decision, was_correct, created_at, agent_code"
        ).in_("agent_code", list(_ARIA_AGENT_CODES))
        q = q.eq("client_id", client_id) if client_id else q.eq("reseller_id", reseller_id)
        r = q.order("created_at", desc=True).limit(limit).execute()
        return r.data or []
    except Exception as e:
        logger.error(
            f"aria_memory_repository.fetch_recent_for_owner failed "
            f"(client_id={client_id}, reseller_id={reseller_id}): {e}",
            exc_info=True,
        )
        return []
