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


def insert_scheduled_posts_bulk(rows: list[dict]) -> list[dict]:
    """INSERT scheduled_posts batch · atómico (single SQL INSERT batch ·
    todos o ninguno · Postgres transaction). DEBT-CL-018.

    Each row debe contener: client_id, social_account_id, content_id,
    scheduled_for (ISO), status='pending', media_url (opcional).
    """
    if not rows:
        return []
    r = _sb().table("scheduled_posts").insert(rows).execute()
    if not r.data or len(r.data) != len(rows):
        raise RuntimeError(
            f"bulk insert returned {len(r.data or [])} rows · expected {len(rows)}"
        )
    return r.data
