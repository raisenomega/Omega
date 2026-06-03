"""SENTINEL Capa 12 · disparar el scan de salud de agentes inline ("Escanear ahora") · owner-only."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_agents_health_worker import run_agents_health_scan


async def handle_agents_health_trigger(authorization: Optional[str]) -> Dict[str, Any]:
    """Corre el scan ahora mismo y devuelve el resultado."""
    await require_superadmin(authorization)
    return await run_agents_health_scan()
