"""Helpers de persistencia ARIA · privado · solo usado por message.py handler.

Centraliza los 4 INSERTs OBLIGATORIOS de cada mensaje ARIA (regla canónica §12):
1. aria_conversations (user message)
2. aria_conversations (assistant message)
3. behavioral_events (event_type='aria_message_sent')
4. agent_memory (agent_code='aria', was_correct=null)
"""
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService


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


def insert_behavioral_event(supabase: SupabaseService, user_id: str, client_id: str, event_type: str, event_data: Optional[dict] = None) -> Optional[str]:
    """Retorna event_id si fue insertado (para trazabilidad agent_memory.source_event_id)."""
    resp = supabase.client.table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id,
        "event_type": event_type, "event_data": event_data,
    }).execute()
    return resp.data[0]["id"] if resp.data else None


def insert_agent_memory(supabase: SupabaseService, client_id: str, content: str, source_event_id: Optional[str]) -> None:
    """INSERT agent_memory (agent_code='aria', was_correct=null) · cierre a 72h por cron."""
    supabase.client.table("agent_memory").insert({
        "client_id": client_id, "agent_code": "aria", "content": content,
        "was_correct": None, "source_event_id": source_event_id,
    }).execute()


def load_recent_history(supabase: SupabaseService, user_id: str, window: int) -> list[dict]:
    """Carga últimos N mensajes (ASC) para construir context de Claude."""
    resp = supabase.client.table("aria_conversations").select(
        "role, content, created_at"
    ).eq("user_id", user_id).order("created_at", desc=True).limit(window).execute()
    rows = list(reversed(resp.data or []))
    return [{"role": r["role"], "content": r["content"]} for r in rows]
