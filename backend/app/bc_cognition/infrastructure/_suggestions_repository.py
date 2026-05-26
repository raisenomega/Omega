"""Lecturas de señales reales para las reglas de ARIA Suggestions · service_role · A1/A9.

Split (C4): el CRUD de la tabla aria_suggestions vive en _suggestions_writer.
Acá solo se leen señales de OTRAS tablas (scheduled_posts, client_plans, aria_suggestions
para idempotencia). Best-effort: ante fallo retornan valor que hace NO emitir la regla (P1).
"""
import logging
from datetime import datetime
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_PUBLISHED = ("published", "published_manual")


def _sb() -> Any:
    return get_supabase_service().client


def published_signal(client_id: str) -> tuple[bool, Optional[datetime]]:
    """Señal para inactivity → (determinable, last_published_at): (False,None)=consulta falló
    (P1: no emitir) · (True,None)=nunca publicó (aplica) · (True,dt)=fecha del último publicado."""
    try:
        r = (_sb().table("scheduled_posts").select("scheduled_for")
             .eq("client_id", client_id).in_("status", list(_PUBLISHED))
             .order("scheduled_for", desc=True).limit(1).execute())
        if not r.data:
            return (True, None)
        raw = r.data[0].get("scheduled_for")
        return (True, datetime.fromisoformat(raw.replace("Z", "+00:00")) if raw else None)
    except Exception as e:
        logger.error(f"_suggestions_repository.published_signal failed: {e}", exc_info=True)
        return (False, None)


def client_plan(client_id: str) -> Optional[str]:
    """Valor de client_plans.plan · None si no hay fila O fallo (indeterminado · P1)."""
    try:
        r = _sb().table("client_plans").select("plan").eq("client_id", client_id).limit(1).execute()
        return r.data[0].get("plan") if r.data else None
    except Exception as e:
        logger.error(f"_suggestions_repository.client_plan failed: {e}", exc_info=True)
        return None


def unread_type_exists(client_id: str, suggestion_type: str) -> bool:
    """Idempotencia: True si ya hay una sugerencia is_read=false de ese tipo para el cliente.
    Fail-safe a True (ante fallo NO insertamos duplicado · conservador · P1)."""
    try:
        r = (_sb().table("aria_suggestions").select("id")
             .eq("client_id", client_id).eq("suggestion_type", suggestion_type)
             .eq("is_read", False).limit(1).execute())
        return bool(r.data)
    except Exception as e:
        logger.error(f"_suggestions_repository.unread_type_exists failed: {e}", exc_info=True)
        return True
