"""Repository content_lab_v3 · única capa de WRITE/READ a content_lab_generated."""
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"content_lab_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def find_client_for_user(user_id: str) -> Optional[dict[str, Any]]:
    """Cliente propio del usuario (incluye industry + brand_voice)."""
    r = _sb().table("clients").select("id, name, industry, brand_voice, target_audience").eq("user_id", user_id).limit(1).execute()
    return r.data[0] if r.data else None


def find_client_context(client_id: str) -> dict[str, Any]:
    """Carga client_context para system prompt (tono, keywords, audiencia)."""
    r = _sb().table("client_context").select(
        "tone, brand_voice, target_audience, audience_age_range, primary_goal"
    ).eq("client_id", client_id).limit(1).execute()
    return r.data[0] if r.data else {}


def insert_generated_content(client_id: str, payload: dict[str, Any]) -> Optional[str]:
    """INSERT content_lab_generated · retorna id del nuevo draft."""
    r = _sb().table("content_lab_generated").insert({**payload, "client_id": client_id}).execute()
    return str(r.data[0]["id"]) if r.data else None


def find_client_plan(client_id: str) -> str:
    """Retorna 'adopcion'|'basic'|'pro'|'enterprise' · default 'adopcion' si no row."""
    r = _sb().table("client_plans").select("plan").eq("client_id", client_id).limit(1).execute()
    return r.data[0]["plan"] if r.data else "adopcion"
