"""Repository ARIA · única capa que toca Supabase para ARIA reads/writes.

Análogo a memory_repository (BC_COGNITION §3). Use cases (application)
llaman aquí · jamás SDK Supabase directo en handlers.
"""
from typing import Any, Optional
from app.infrastructure.supabase_service import SupabaseService


def find_client_by_user(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    r = supabase.client.table("clients").select("id, aria_level").eq("user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def find_reseller_by_owner(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    r = supabase.client.table("resellers").select("id").eq("owner_user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def insert_user_message(supabase: SupabaseService, user_id: str, client_id: Optional[str], content: str, level: int) -> None:
    supabase.client.table("aria_conversations").insert({
        "user_id": user_id, "client_id": client_id, "role": "user",
        "content": content, "aria_level": level,
    }).execute()


def insert_assistant_message(supabase: SupabaseService, user_id: str, client_id: Optional[str], content: str, level: int) -> None:
    supabase.client.table("aria_conversations").insert({
        "user_id": user_id, "client_id": client_id, "role": "assistant",
        "content": content, "aria_level": level,
    }).execute()


def insert_behavioral_event(
    supabase: SupabaseService, user_id: str,
    client_id: Optional[str], reseller_id: Optional[str],
    event_type: str, event_data: Optional[dict] = None,
    session_id: Optional[str] = None,
) -> Optional[str]:
    """Persiste signal · cliente O reseller (chk_behavioral_owner_present)."""
    r = supabase.client.table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id, "reseller_id": reseller_id,
        "event_type": event_type, "event_data": event_data, "session_id": session_id,
    }).execute()
    return r.data[0]["id"] if r.data else None


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
        "context": user_message, "decision": assistant_response, "confidence": 7,
        "was_correct": was_correct, "source_event_id": source_event_id,
        "metadata": {"aria_level": level},
    }).execute()


def load_recent_history(supabase: SupabaseService, user_id: str, window: int) -> list[dict[str, str]]:
    """Últimos N mensajes (ASC) para context window de Claude."""
    r = supabase.client.table("aria_conversations").select(
        "role, content, created_at"
    ).eq("user_id", user_id).order("created_at", desc=True).limit(window).execute()
    return [{"role": x["role"], "content": x["content"]} for x in reversed(r.data or [])]


def load_history_for_endpoint(supabase: SupabaseService, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Historial completo ASC para GET /history endpoint."""
    r = supabase.client.table("aria_conversations").select(
        "role, content, aria_level, created_at"
    ).eq("user_id", user_id).order("created_at", desc=False).limit(limit).execute()
    return r.data or []
