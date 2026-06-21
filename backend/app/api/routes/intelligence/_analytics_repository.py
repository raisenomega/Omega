"""Lecturas per-negocio para Analytics social (Zernio) · service_role · read-only · best-effort."""
import logging
from typing import Any, Dict, List, Optional

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb() -> Any:
    return get_supabase_service().client


def get_zernio_profile_id(client_id: str) -> Optional[str]:
    """`clients.zernio_profile_id` del negocio (scope per-negocio de daily-metrics/best-time)."""
    try:
        r = _sb().table("clients").select("zernio_profile_id").eq("id", client_id).limit(1).execute()
        return r.data[0].get("zernio_profile_id") if r.data else None
    except Exception as e:
        logger.error(f"get_zernio_profile_id failed: {e}", exc_info=True)
        return None


def get_zernio_accounts(client_id: str) -> List[Dict[str, str]]:
    """Cuentas vinculadas del negocio (platform + account_id) · solo zernio_account_id NOT NULL.
    AISLAMIENTO: filtra por client_id → nunca trae cuentas de otro negocio."""
    try:
        r = (_sb().table("social_accounts").select("platform, zernio_account_id")
             .eq("client_id", client_id).not_.is_("zernio_account_id", "null").execute())
        return [{"platform": str(x.get("platform") or ""), "account_id": str(x["zernio_account_id"])}
                for x in (r.data or []) if x.get("zernio_account_id")]
    except Exception as e:
        logger.error(f"get_zernio_accounts failed: {e}", exc_info=True)
        return []
