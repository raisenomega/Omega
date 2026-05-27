"""Repository reads/writes · publishing · DDD A1/A9.

Única capa de acceso a scheduled_posts / content_lab_generated / social_accounts
para el flujo de auto-publicación. I/O sync envuelto en to_thread por el service.
"""
import logging
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb() -> Any:
    return get_supabase_service().client


def get_scheduled_post(post_id: str) -> Optional[dict[str, Any]]:
    """Fila cruda de scheduled_posts · None si no existe."""
    r = _sb().table("scheduled_posts").select("*").eq("id", post_id).limit(1).execute()
    return r.data[0] if r.data else None


def get_content_text(content_id: str) -> str:
    """Texto generado del content_lab · '' si no existe (post sin contenido textual)."""
    r = (_sb().table("content_lab_generated")
         .select("generated_text").eq("id", content_id).limit(1).execute())
    if not r.data:
        return ""
    return str(r.data[0].get("generated_text") or "")


def get_account_platform(social_account_id: str) -> Optional[str]:
    """Platform de la social_account asociada al post · None si no existe."""
    r = (_sb().table("social_accounts")
         .select("platform").eq("id", social_account_id).limit(1).execute())
    if not r.data:
        return None
    return str(r.data[0].get("platform") or "") or None


def mark_publishing(post_id: str) -> None:
    """Transición pending → publishing (lock optimista · in-flight)."""
    _sb().table("scheduled_posts").update({"status": "publishing"}).eq("id", post_id).execute()


def mark_published(post_id: str, platform_post_id: str) -> dict[str, Any]:
    """Éxito real confirmado por Meta · persiste el id del post en la plataforma.
    Raise si 0 filas (no miente éxito sin persistir · P1)."""
    r = (_sb().table("scheduled_posts")
         .update({"status": "published", "platform_post_id": platform_post_id, "error_message": None})
         .eq("id", post_id).execute())
    if not r.data:
        raise RuntimeError(f"mark_published affected 0 rows · post_id={post_id}")
    return r.data[0]


def mark_failed(post_id: str, error_message: str) -> None:
    """Fallo real de la publicación · registra el error honesto. Best-effort
    (si la escritura del error falla, ya quedó logueado por el service)."""
    _sb().table("scheduled_posts").update(
        {"status": "failed", "error_message": error_message[:500]},
    ).eq("id", post_id).execute()
