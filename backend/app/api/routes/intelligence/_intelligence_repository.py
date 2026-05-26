"""Repository Intelligence · caché read-through 24h sobre analytics_snapshots.

RESILIENTE (decisión 3): toda lectura/escritura va envuelta en try/except ·
si la tabla no existe aún (migración 00027 sin aplicar) o falla la red →
log warning + degrada (None / no-op) · NUNCA rompe el endpoint.
Escritura best-effort (caché · no crítica).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
_CACHE_TTL = timedelta(hours=24)


def _sb():
    return get_supabase_service().client


def _parse_ts(raw: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def get_fresh_snapshot(client_id: str, snapshot_type: str) -> Optional[dict[str, Any]]:
    """Snapshot más reciente con <24h · None si no hay/expiró/error (resiliente)."""
    try:
        r = (
            _sb().table("analytics_snapshots")
            .select("payload, score, created_at")
            .eq("client_id", client_id).eq("snapshot_type", snapshot_type)
            .order("created_at", desc=True).limit(1).execute()
        )
    except Exception as e:
        logger.warning(f"get_fresh_snapshot fallback ({snapshot_type}/{client_id}): {e}")
        return None
    if not r.data:
        return None
    row = r.data[0]
    created = _parse_ts(row.get("created_at", ""))
    if created is None:
        return None
    if datetime.now(timezone.utc) - created > _CACHE_TTL:
        return None
    return row


def save_snapshot(
    client_id: str, snapshot_type: str, payload: dict[str, Any], score: Optional[int]
) -> None:
    """INSERT best-effort en analytics_snapshots · log + continue si falla."""
    try:
        _sb().table("analytics_snapshots").insert({
            "client_id": client_id, "snapshot_type": snapshot_type,
            "payload": payload, "score": score,
        }).execute()
    except Exception as e:
        logger.warning(f"save_snapshot fallback ({snapshot_type}/{client_id}): {e}")


def get_client_site(client_id: str) -> dict[str, Any]:
    """name/website/region/industry del cliente · {} si no existe o error (resiliente)."""
    try:
        r = (
            _sb().table("clients")
            .select("name, website, region, industry")
            .eq("id", client_id).limit(1).execute()
        )
    except Exception as e:
        logger.warning(f"get_client_site fallback ({client_id}): {e}")
        return {}
    return r.data[0] if r.data else {}
