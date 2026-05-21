"""Repository ARIA memory · agent_memory inserts + delete history.

Separado de aria_repository (DDD A1/A9 · C4 split a ≤75L).
"""
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService


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


def delete_aria_history(supabase: SupabaseService, user_id: str) -> None:
    """DELETE aria_conversations WHERE user_id · Settings ARIA tab."""
    supabase.client.table("aria_conversations").delete().eq("user_id", user_id).execute()
