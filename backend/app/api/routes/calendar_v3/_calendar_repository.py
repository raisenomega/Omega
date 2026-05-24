"""Repository writes · calendar_v3 · DDD A1/A9."""
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort wrapper · errores loguean y NO propagan."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        logger.error(f"calendar_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def update_status(post_id: str, value: str) -> None:
    _sb().table("scheduled_posts").update({"status": value}).eq("id", post_id).execute()


def insert_behavioral_status_change(user_id: str, client_id: str, post_id: str, from_status: str, to_status: str) -> None:
    _sb().table("behavioral_events").insert({
        "user_id": user_id, "client_id": client_id,
        "event_type": "post_status_changed",
        "event_data": {"post_id": post_id, "from_status": from_status, "to_status": to_status},
    }).execute()


def insert_scheduled_post(
    client_id: str,
    social_account_id: str,
    content_id: str,
    scheduled_for_iso: str,
    media_url: str | None,
) -> dict:
    """INSERT scheduled_posts con schema V3 real · DEBT-CL-017 + path X.
    Status inicial 'pending' (per migración 00001 CHECK constraint).
    Retorna la row creada."""
    r = _sb().table("scheduled_posts").insert({
        "client_id": client_id,
        "social_account_id": social_account_id,
        "content_id": content_id,
        "scheduled_for": scheduled_for_iso,
        "status": "pending",
        "media_url": media_url,
    }).execute()
    if not r.data:
        raise RuntimeError("scheduled_posts insert returned no row")
    return r.data[0]
