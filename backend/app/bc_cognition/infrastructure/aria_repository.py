"""Repository ARIA · Supabase conversación + behavioral · DDD A1/A9. safe_insert best-effort (log+None · FIX 4)."""
import asyncio, logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import SupabaseService
from app.bc_cognition.domain.aria_history import clean_history
from app.bc_cognition.infrastructure.aria_plan_repository import fetch_live_plan

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


async def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"aria_repository.{label} failed: {e}", exc_info=True)
        return None


def find_client_by_user(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    r = supabase.client.table("clients").select("id, aria_level").eq("user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def find_reseller_by_owner(supabase: SupabaseService, user_id: str) -> Optional[dict[str, Any]]:
    # DEBT-046: include aria_level so _resolve_role can return the real purchased level.
    r = supabase.client.table("resellers").select("id, aria_level").eq("owner_user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def fetch_aria_context(supabase: SupabaseService, client_id: str) -> Optional[dict[str, Any]]:
    """Contexto enriquecido ARIA: client_context + social + identidad + assets/samples. Best-effort: None si no hay context."""
    try:
        r = supabase.client.table("client_context").select("*").eq("client_id", client_id).limit(1).execute()
        if not r.data:
            return None
        ctx: dict[str, Any] = r.data[0]
        sa = supabase.client.table("social_accounts").select("platform, account_name").eq("client_id", client_id).execute()
        ctx["social_accounts"] = sa.data or []
        cl = supabase.client.table("clients").select("name, industry, region, website, business_email").eq("id", client_id).limit(1).execute()
        ctx["_client"] = cl.data[0] if cl.data else {}
        ba = supabase.client.table("client_brand_assets").select("primary_color, secondary_color, accent_color, font_primary, font_secondary, logo_file_id").eq("client_id", client_id).limit(1).execute()
        ctx["_brand_assets"] = ba.data[0] if ba.data else {}
        logo_id = ctx["_brand_assets"].get("logo_file_id")  # → brand_files.storage_url
        ctx["_logo_url"] = None
        if logo_id:
            bf = supabase.client.table("brand_files").select("storage_url").eq("id", logo_id).limit(1).execute()
            ctx["_logo_url"] = bf.data[0].get("storage_url") if bf.data else None
        sc = supabase.client.table("brand_voice_corpus").select("id", count="exact").eq("client_id", client_id).eq("source", "manual_upload").execute()
        ctx["_samples_count"] = sc.count or 0
        fetch_live_plan(supabase, client_id, ctx)  # FASE 0b · plan/posts/credits (aria_plan_repository · C4)
        return ctx
    except Exception as e:
        logger.error(f"aria_repository.fetch_aria_context failed: {e}", exc_info=True)
        return None


def _insert_msg(supabase: SupabaseService, user_id: str, client_id: Optional[str], role: str, content: str, level: int) -> None:
    supabase.client.table("aria_conversations").insert(
        {"user_id": user_id, "client_id": client_id, "role": role, "content": content, "aria_level": level}).execute()


def insert_user_message(supabase: SupabaseService, user_id: str, client_id: Optional[str], content: str, level: int) -> None:
    _insert_msg(supabase, user_id, client_id, "user", content, level)


def insert_assistant_message(supabase: SupabaseService, user_id: str, client_id: Optional[str], content: str, level: int) -> None:
    _insert_msg(supabase, user_id, client_id, "assistant", content, level)


def insert_behavioral_event(
    supabase: SupabaseService, user_id: str, client_id: Optional[str], reseller_id: Optional[str],
    event_type: str, event_data: Optional[dict] = None, session_id: Optional[str] = None,
) -> Optional[str]:
    """Persiste signal · client_id OR reseller_id (chk_behavioral_owner_present)."""
    r = supabase.client.table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id, "reseller_id": reseller_id,
        "event_type": event_type, "event_data": event_data, "session_id": session_id,
    }).execute()
    return r.data[0]["id"] if r.data else None


def _conv_query(supabase: SupabaseService, user_id: str, client_id: Optional[str], cols: str):
    # SELECT aria_conversations del user · Switcher V1: client_id → scope a ese negocio (ausente = todo, legacy)
    q = supabase.client.table("aria_conversations").select(cols).eq("user_id", user_id)
    return q.eq("client_id", client_id) if client_id else q


def load_recent_history(supabase: SupabaseService, user_id: str, window: int, client_id: Optional[str] = None) -> list[dict[str, str]]:
    try:  # fallo de DB → [] · ARIA nunca cae por el historial (window*2 → clean_history)
        r = _conv_query(supabase, user_id, client_id, "role, content, created_at").order("created_at", desc=True).limit(window * 2).execute()
        return clean_history([{"role": x["role"], "content": x["content"]} for x in reversed(r.data or [])], window)
    except Exception as e:
        logger.error(f"load_recent_history failed: {e}", exc_info=True); return []


def load_history_for_endpoint(supabase: SupabaseService, user_id: str, limit: int = 50, client_id: Optional[str] = None) -> list[dict[str, Any]]:
    # DESC+limit = últimos N · reversed = ASC
    r = _conv_query(supabase, user_id, client_id, "role, content, aria_level, created_at").order("created_at", desc=True).limit(limit).execute()
    return list(reversed(r.data or []))
