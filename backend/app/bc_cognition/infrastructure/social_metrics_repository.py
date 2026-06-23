"""Repository social_metrics · negocios activos + upsert idempotente (Arco 1 · Fase 2).
Pattern: free functions + _sb() service-role singleton (BYPASSRLS · escritura backend)."""
import logging
from typing import Any, Dict, List

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def _sb():
    return get_supabase_service().client


def fetch_active_profiles() -> List[Dict[str, str]]:
    """Negocios con profile Zernio (los que el snapshot puede resolver). [{client_id, profile_id}]."""
    try:
        r = (_sb().table("clients").select("id, zernio_profile_id")
             .not_.is_("zernio_profile_id", "null").execute())
        return [{"client_id": str(row["id"]), "profile_id": str(row["zernio_profile_id"])}
                for row in (r.data or [])]
    except Exception as e:
        logger.error(f"fetch_active_profiles failed: {e}", exc_info=True)
        return []


def upsert_social_metrics(rows: List[Dict[str, Any]]) -> int:
    """UPSERT por (client_id, platform, metric_date) = idempotente (re-correr no duplica). 0 si vacío.

    captured_at NO va en el payload → en conflicto conserva la PRIMERA captura (por diseño · Opción 3).
    La señal de freshness es metric_date (día nuevo = INSERT fresco), NO captured_at: una re-corrida
    del mismo día es idempotente e invisible en captured_at — esperado, no deuda."""
    if not rows:
        return 0
    try:
        _sb().table("social_metrics").upsert(
            rows, on_conflict="client_id,platform,metric_date").execute()
        return len(rows)
    except Exception as e:
        logger.error(f"upsert_social_metrics failed · {len(rows)} filas: {e}", exc_info=True)
        return 0
