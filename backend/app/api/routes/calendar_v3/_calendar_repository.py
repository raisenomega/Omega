"""Repository writes · calendar_v3 · DDD A1/A9."""
import asyncio
import logging
from typing import Any, Callable, Optional, ParamSpec, TypeVar
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
P = ParamSpec("P"); T = TypeVar("T")


async def safe_insert(label: str, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> Optional[T]:
    """Best-effort wrapper · errores loguean y NO propagan. DEBT-074: async to_thread."""
    try:
        return await asyncio.to_thread(fn, *args, **kwargs)
    except Exception as e:
        logger.error(f"calendar_repository.{label} failed: {e}", exc_info=True)
        return None


def _sb():
    return get_supabase_service().client


def update_status(post_id: str, value: str) -> dict:
    """UPDATE status · retorna la fila persistida · raise si 0 filas (post inexistente
    o CHECK violado) para que el handler NO mienta 200 sin persistir (P1)."""
    r = _sb().table("scheduled_posts").update({"status": value}).eq("id", post_id).execute()
    if not r.data:
        raise RuntimeError(f"update_status affected 0 rows · post_id={post_id} · value={value}")
    return r.data[0]


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
