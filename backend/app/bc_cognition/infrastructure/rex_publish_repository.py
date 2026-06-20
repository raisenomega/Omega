"""Repository REX · todo el acceso a datos del publicador autónomo (DDD A1/A9).

Mantiene el use case libre de SQL (espejo de _publish_repository). Corre con
service_role. I/O sync · el use case lo envuelve en asyncio.to_thread.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_TRUE = {"1", "true", "yes", "on"}


def _sb() -> Any:
    return get_supabase_service().client


def rex_live_enabled() -> bool:
    """Flag maestro · REX solo publica de verdad si está ON (default OFF · inerte en prod).
    No entra en config.py (archivo en el techo C4 100L) · env directo en infra (capa de I/O)."""
    return os.getenv("REX_LIVE_ENABLED", "").strip().lower() in _TRUE


def fetch_active_rex_client_ids() -> list[str]:
    """client_ids con add-on comprado Y toggle encendido (el universo que REX recorre)."""
    r = (_sb().table("clients").select("id")
         .eq("rex_addon_active", True).eq("autonomous_mode_on", True).execute())
    return [str(row["id"]) for row in (r.data or [])]


def fetch_client_gating(client_id: str) -> Optional[dict[str, Any]]:
    """Flags + identidad del cliente · None si no se pudo leer (caller = fail-safe, no evalúa)."""
    try:
        r = (_sb().table("clients")
             .select("rex_addon_active, autonomous_mode_on, crisis_active, user_id, reseller_id")
             .eq("id", client_id).limit(1).execute())
        return r.data[0] if r.data else None
    except Exception as e:
        logger.error(f"rex.fetch_client_gating failed client={client_id}: {e}", exc_info=True)
        return None


def fetch_due_posts(client_id: str, limit: int) -> list[dict[str, Any]]:
    """scheduled_posts 'pending' con scheduled_for <= ahora · cronológico · reusa idx status_time."""
    now = datetime.now(timezone.utc).isoformat()
    r = (_sb().table("scheduled_posts")
         .select("id, content_id, social_account_id, scheduled_for, media_url")
         .eq("client_id", client_id).eq("status", "pending")
         .lte("scheduled_for", now).order("scheduled_for").limit(limit).execute())
    return r.data or []


def fetch_content_signals(content_id: str) -> dict[str, Any]:
    """confidence + brand_voice_score del content · {} si no existe (caller = fail-safe hold)."""
    try:
        r = (_sb().table("content_lab_generated")
             .select("confidence, brand_voice_score").eq("id", content_id).limit(1).execute())
        return r.data[0] if r.data else {}
    except Exception as e:
        logger.error(f"rex.fetch_content_signals failed content={content_id}: {e}", exc_info=True)
        return {}


def fetch_account_binding(social_account_id: str) -> dict[str, Any]:
    """platform + zernio_account_id de la cuenta · {} si no existe (caller = hold connection)."""
    try:
        r = (_sb().table("social_accounts")
             .select("platform, zernio_account_id, status").eq("id", social_account_id).limit(1).execute())
        return r.data[0] if r.data else {}
    except Exception as e:
        logger.error(f"rex.fetch_account_binding failed sa={social_account_id}: {e}", exc_info=True)
        return {}


def count_published_today(client_id: str) -> int:
    """Publicaciones REX REALES de hoy (gate_result='publish' AND published_at NOT NULL).
    Autoridad propia · NO cuenta publish manual (otra vía · no toca rex_publish_log)."""
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    r = (_sb().table("rex_publish_log").select("id", count="exact")
         .eq("client_id", client_id).eq("gate_result", "publish")
         .not_.is_("published_at", "null").gte("created_at", start).execute())
    return r.count or 0


def insert_rex_publish_log(row: dict[str, Any]) -> None:
    """Append-only · best-effort (un fallo del log NO debe romper el ciclo de publicación)."""
    try:
        _sb().table("rex_publish_log").insert(row).execute()
    except Exception as e:
        logger.error(f"rex.insert_rex_publish_log failed: {e}", exc_info=True)
