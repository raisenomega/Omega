"""SENTINEL Capa 3 · disparar el scan Red/HTTP ahora ("Escanear ahora") · owner-only."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_network_http_worker import run_network_http_scan


async def handle_network_http_trigger(authorization: Optional[str]) -> Dict[str, Any]:
    """Corre el scan ahora mismo y devuelve el resultado."""
    await require_superadmin(authorization)
    return await run_network_http_scan()
