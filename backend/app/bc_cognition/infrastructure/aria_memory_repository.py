"""Repository ARIA memory · agent_memory inserts + reads + delete history.

Separado de aria_repository (DDD A1/A9 · C4 split a ≤75L).
T4 Sprint 1: fetch_recent_for_owner agregado para inyectar memoria al system.
"""
import logging
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService
from app.bc_cognition.domain.input_threats import redact_pii
from app.bc_cognition.infrastructure.voyage_adapter import embed_texts

logger = logging.getLogger(__name__)

_ARIA_AGENT_CODES = ("aria", "aria_1", "aria_2", "aria_3", "aria_4")


def _embed_memory(context: str) -> Optional[list[float]]:
    """DEBT-048: embedding best-effort. None si Voyage no disponible → columna NULL.
    Corre dentro del to_thread de safe_insert · blocking OK · nunca rompe el write."""
    vecs = embed_texts([context], "document")
    return vecs[0] if vecs else None


def insert_agent_memory(
    supabase: SupabaseService, user_id: str,
    client_id: Optional[str], reseller_id: Optional[str],
    user_message: str, assistant_response: str, level: int,
    source_event_id: Optional[str], was_correct: Optional[bool] = None,
) -> None:
    """INSERT agent_memory schema M1 · was_correct=None → cron evalúa 72h."""
    context = redact_pii(user_message)[0]
    decision = redact_pii(assistant_response)[0]
    supabase.client.table("agent_memory").insert({
        "user_id": user_id, "client_id": client_id, "reseller_id": reseller_id,
        "agent_code": "aria", "memory_type": "episodic",
        "context": context, "decision": decision, "confidence": 7,
        "was_correct": was_correct, "source_event_id": source_event_id,
        "embedding": _embed_memory(f"{context}\n{decision}"),
        "metadata": {"aria_level": level},
    }).execute()


def delete_aria_history(supabase: SupabaseService, user_id: str, client_id: Optional[str] = None) -> None:
    """DELETE aria_conversations del user · Settings ARIA tab. Switcher V1: client_id → borra
    solo ese negocio (ausente = todo, legacy backward-compat)."""
    q = supabase.client.table("aria_conversations").delete().eq("user_id", user_id)
    if client_id:
        q = q.eq("client_id", client_id)
    q.execute()


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


def fetch_similar_for_owner(
    supabase: SupabaseService, query: str,
    client_id: Optional[str] = None, limit: int = 10,
) -> list[dict]:
    """DEBT-048: top-k memorias semánticamente relevantes a `query` (RPC find_similar_memories).
    Best-effort: [] si no hay embedding (Voyage down), RPC falla o cero resultados →
    el caller cae a fetch_recent_for_owner (cronológico). Filtra agent_code='aria' + client_id."""
    if not client_id:
        return []
    vecs = embed_texts([query], "query")
    if not vecs:
        return []
    try:
        r = supabase.client.rpc("find_similar_memories", {
            "query_embedding": vecs[0], "target_agent_code": "aria",
            "target_client_id": client_id, "limit_count": limit,
        }).execute()
        return r.data or []
    except Exception as e:
        logger.error(f"aria_memory_repository.fetch_similar_for_owner failed: {e}", exc_info=True)
        return []
