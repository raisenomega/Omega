"""SENTINEL Capa 11 · disparar el scan de integraciones ahora ("Escanear ahora") · owner-only."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_integrations_worker import run_integrations_scan


async def handle_integrations_trigger(authorization: Optional[str]) -> Dict[str, Any]:
    """Corre el scan ahora mismo y devuelve el resultado."""
    await require_superadmin(authorization)
    return await run_integrations_scan()
