"""Repository REX · datos del publicador autónomo (DDD A1/A9 · service_role · I/O sync→to_thread)."""
import logging
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.infrastructure import owner_accounts_repository as owners

logger = logging.getLogger(__name__)


def _sb() -> Any:
    return get_supabase_service().client


def fetch_active_rex_client_ids() -> list[str]:
    """Universo REX: (add-on comprado OR cuenta-dueño exenta) Y toggle encendido.
    El toggle filtra server-side en el query · el add-on EFECTIVO se resuelve con OR owners."""
    owner_ids = owners.fetch_owner_user_ids()
    r = (_sb().table("clients").select("id, rex_addon_active, user_id")
         .eq("autonomous_mode_on", True).execute())
    return [str(row["id"]) for row in (r.data or [])
            if row.get("rex_addon_active") or str(row.get("user_id")) in owner_ids]


def fetch_client_gating(client_id: str) -> Optional[dict[str, Any]]:
    """Flags + identidad del cliente · None si no se pudo leer (caller = fail-safe, no evalúa).
    rex_addon_active EFECTIVO = almacenado OR cuenta-dueño exenta (owner_accounts · migr 00074)."""
    try:
        r = (_sb().table("clients")
             .select("rex_addon_active, autonomous_mode_on, crisis_active, user_id, reseller_id")
             .eq("id", client_id).limit(1).execute())
        if not r.data:
            return None
        row = r.data[0]
        row["rex_addon_active"] = (bool(row.get("rex_addon_active"))
                                   or str(row.get("user_id")) in owners.fetch_owner_user_ids())
        return row
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


def count_published_today_by_platform(client_id: str) -> dict[str, int]:
    """Publicaciones REX REALES de hoy POR RED (gate_result='publish' AND published_at NOT NULL · autoridad propia)."""
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    r = (_sb().table("rex_publish_log").select("platform")
         .eq("client_id", client_id).eq("gate_result", "publish")
         .not_.is_("published_at", "null").gte("created_at", start).execute())
    return dict(Counter(str(row.get("platform") or "") for row in (r.data or [])))


def insert_rex_publish_log(row: dict[str, Any]) -> None:
    """Append-only · best-effort (un fallo del log NO debe romper el ciclo de publicación)."""
    try:
        _sb().table("rex_publish_log").insert(row).execute()
    except Exception as e:
        logger.error(f"rex.insert_rex_publish_log failed: {e}", exc_info=True)
