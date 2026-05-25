"""Repository ARIA · capa Supabase para conversación + behavioral · DDD A1/A9.

safe_insert: best-effort wrapper · log + return None (FIX 4 audit).
Memory + delete history: ver aria_memory_repository (C4 split).
"""
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"aria_repository.{label} failed: {e}", exc_info=True)
        return None


def find_client_by_user(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    r = supabase.client.table("clients").select("id, aria_level").eq("user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def find_reseller_by_owner(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    r = supabase.client.table("resellers").select("id").eq("owner_user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def fetch_client_context(supabase: SupabaseService, client_id: str) -> Optional[dict[str, Any]]:
    """Lee client_context para inyectar a ARIA (BUG 2). Best-effort: None si falla/vacío."""
    try:
        r = supabase.client.table("client_context").select(
            "niche, vertical, business_what, target_audience, uploaded_context_text"
        ).eq("client_id", client_id).limit(1).execute()
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(f"aria_repository.fetch_client_context failed: {e}", exc_info=True)
        return None


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
    """Persiste signal · client_id OR reseller_id (chk_behavioral_owner_present)."""
    r = supabase.client.table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id, "reseller_id": reseller_id,
        "event_type": event_type, "event_data": event_data, "session_id": session_id,
    }).execute()
    return r.data[0]["id"] if r.data else None


def load_recent_history(supabase: SupabaseService, user_id: str, window: int) -> list[dict[str, str]]:
    r = supabase.client.table("aria_conversations").select(
        "role, content, created_at"
    ).eq("user_id", user_id).order("created_at", desc=True).limit(window).execute()
    return [{"role": x["role"], "content": x["content"]} for x in reversed(r.data or [])]


def load_history_for_endpoint(supabase: SupabaseService, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
    r = supabase.client.table("aria_conversations").select(
        "role, content, aria_level, created_at"
    ).eq("user_id", user_id).order("created_at", desc=False).limit(limit).execute()
    return r.data or []
