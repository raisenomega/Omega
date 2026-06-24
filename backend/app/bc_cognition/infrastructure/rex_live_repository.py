"""Repository REX · llaves del modo LIVE (maestro global + flag por-reseller).

Extraído de rex_publish_repository (Split Opción 1 · C4 ≤100L). Self-contained:
NO importa rex_publish_repository (evita ciclo). I/O sync→to_thread en el caller.
"""
import logging
import os
from typing import Any
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_TRUE = {"1", "true", "yes", "on"}


def _sb() -> Any:
    return get_supabase_service().client


def rex_live_enabled() -> bool:
    """Maestro global · REX publica solo si ON (default OFF · env directo · no entra en config.py por C4)."""
    return os.getenv("REX_LIVE_ENABLED", "").strip().lower() in _TRUE


def reseller_rex_live(client_id: str) -> bool:
    """2da llave: ¿el reseller DUEÑO del cliente tiene rex_live_enabled=true? · fail-safe False."""
    try:
        c = _sb().table("clients").select("reseller_id").eq("id", client_id).limit(1).execute()
        rid = c.data[0].get("reseller_id") if c.data else None
        r = _sb().table("resellers").select("rex_live_enabled").eq("id", str(rid)).limit(1).execute()
        return bool(r.data and r.data[0].get("rex_live_enabled"))
    except Exception as e:
        logger.error(f"rex.reseller_rex_live failed client={client_id}: {e}", exc_info=True)
        return False
