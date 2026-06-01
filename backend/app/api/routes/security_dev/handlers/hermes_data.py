"""GET /security-dev/hermes · estado actual de salud de las integraciones externas (HERMES).

Última fila por integración de mcp_health_log (patrón latest-per-group de get_status.py):
trae ordenado por checked_at DESC y se queda con el 1er match de cada integration."""
import logging
from typing import Optional, Dict, Any
from app.api.routes.auth.super_owner import require_super_owner
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_FETCH_LIMIT = 200  # suficiente para cubrir las últimas corridas de las 7 integraciones


async def handle_hermes_data(authorization: Optional[str]) -> Dict[str, Any]:
    await require_super_owner(authorization)
    sb = get_supabase_service().client
    try:
        r = sb.table("mcp_health_log") \
            .select("integration, status, last_use, checked_at") \
            .order("checked_at", desc=True) \
            .limit(_FETCH_LIMIT) \
            .execute()
        latest_by_integration: Dict[str, Any] = {}
        for row in (r.data or []):
            integ = row.get("integration")
            if integ and integ not in latest_by_integration:
                latest_by_integration[integ] = row  # 1er match por DESC = más reciente
        integrations = list(latest_by_integration.values())
        return {"integrations": integrations, "count": len(integrations)}
    except Exception as e:
        logger.error(f"handle_hermes_data failed: {e}", exc_info=True)
        return {"integrations": [], "count": 0, "error": str(e)}
