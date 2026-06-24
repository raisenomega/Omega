"""Repository owner_accounts · cuentas-dueño exentas de paywall/add-on REX (migr 00074).

Lectura service-role (la tabla es service-role only · RLS). Exime de PAGOS, NUNCA de
aislamiento. Fail-safe: si la lectura falla → set() vacío (nadie exento · el paywall manda;
exención que falla NUNCA abre una puerta de más). I/O sync→to_thread en el caller.
"""
import logging
from typing import Any
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb() -> Any:
    return get_supabase_service().client


def fetch_owner_user_ids() -> set[str]:
    """user_ids del dueño exentos · fail-safe set() vacío si la lectura falla (nadie exento)."""
    try:
        r = _sb().table("owner_accounts").select("user_id").execute()
        return {str(row["user_id"]) for row in (r.data or []) if row.get("user_id")}
    except Exception as e:
        logger.error(f"owner.fetch_owner_user_ids failed: {e}", exc_info=True)
        return set()
