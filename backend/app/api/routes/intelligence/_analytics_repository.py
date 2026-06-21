"""Lecturas per-negocio para Analytics social (Zernio) · service_role · read-only · best-effort.

Analytics resuelve por **profileId** (la llave canónica · ver DEBT-ANALYTICS-RESOLVER-PROFILEID): el único
dato de DB que necesita es `clients.zernio_profile_id`. Las cuentas + métricas salen de Zernio filtradas por
ese profileId (no de `social_accounts.zernio_account_id`, que es frágil/vacío en negocios sin binding).
"""
import logging
from typing import Any, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb() -> Any:
    return get_supabase_service().client


def get_zernio_profile_id(client_id: str) -> Optional[str]:
    """`clients.zernio_profile_id` del negocio (la llave canónica de resolución per-negocio)."""
    try:
        r = _sb().table("clients").select("zernio_profile_id").eq("id", client_id).limit(1).execute()
        return r.data[0].get("zernio_profile_id") if r.data else None
    except Exception as e:
        logger.error(f"get_zernio_profile_id failed: {e}", exc_info=True)
        return None
