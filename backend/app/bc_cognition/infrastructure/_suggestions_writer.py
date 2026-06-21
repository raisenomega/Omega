"""Writer/reader de la tabla aria_suggestions · service_role · DDD A1/A9 + C4.

Split de _suggestions_repository (que retiene las lecturas de señales para las reglas):
acá vive el CRUD de la propia tabla aria_suggestions (insert/list/get/mark).
service_role bypassa RLS (backend escribe · usuario solo LEE). Best-effort + log.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_COLS = "id, message, suggestion_type, is_read, read_at, created_at"


def _sb() -> Any:
    return get_supabase_service().client


def insert_suggestion(client_id: str, user_id: Optional[str], message: str, suggestion_type: str) -> bool:
    """Inserta una sugerencia con service_role. True si insertó · False si falló."""
    try:
        _sb().table("aria_suggestions").insert({
            "client_id": client_id, "user_id": user_id, "message": message, "suggestion_type": suggestion_type,
        }).execute()
        return True
    except Exception as e:
        logger.error(f"_suggestions_writer.insert_suggestion failed: {e}", exc_info=True)
        return False


def list_suggestions(client_id: str, unread_only: bool) -> list[dict[str, Any]]:
    """Lista del cliente ordenada created_at desc (filtra is_read=false si unread_only)."""
    try:
        q = _sb().table("aria_suggestions").select(_COLS).eq("client_id", client_id)
        if unread_only:
            q = q.eq("is_read", False)
        return q.order("created_at", desc=True).execute().data or []
    except Exception as e:
        logger.error(f"_suggestions_writer.list_suggestions failed: {e}", exc_info=True)
        return []


def get_suggestion(suggestion_id: str) -> Optional[dict[str, Any]]:
    """Trae una sugerencia por id (con client_id para ownership) · None si no existe/falla."""
    try:
        r = (_sb().table("aria_suggestions").select(_COLS + ", client_id")
             .eq("id", suggestion_id).limit(1).execute())
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(f"_suggestions_writer.get_suggestion failed: {e}", exc_info=True)
        return None


def mark_read(suggestion_id: str) -> bool:
    """Marca is_read=true + read_at=now() · True si ok."""
    try:
        _sb().table("aria_suggestions").update({
            "is_read": True, "read_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", suggestion_id).execute()
        return True
    except Exception as e:
        logger.error(f"_suggestions_writer.mark_read failed: {e}", exc_info=True)
        return False


def retract_unread(client_id: str, suggestion_type: str) -> int:
    """Auto-cierra (is_read=true) las unread de este tipo cuya condición ya NO aplica al negocio
    (ej. subió de basic→enterprise → la 'upgrade_plan' caduca). Scope por client_id: NO toca otros
    negocios. Best-effort · 0 si falla (P1)."""
    try:
        _sb().table("aria_suggestions").update({
            "is_read": True, "read_at": datetime.now(timezone.utc).isoformat(),
        }).eq("client_id", client_id).eq("suggestion_type", suggestion_type).eq("is_read", False).execute()
        return 1
    except Exception as e:
        logger.error(f"_suggestions_writer.retract_unread failed: {e}", exc_info=True)
        return 0
