"""SENTINEL Capa 8 · disparar chaos test ahora ("Disparar chaos test") · owner-only."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_chaos_worker import run_chaos_scan


class ChaosTriggerRequest(BaseModel):
    scenarios: Optional[List[str]] = None  # vacío = todos


async def handle_chaos_trigger(request: ChaosTriggerRequest, authorization: Optional[str]) -> Dict[str, Any]:
    """Corre los escenarios (o el subset pedido) ahora mismo y devuelve el resultado."""
    await require_superadmin(authorization)
    return await run_chaos_scan(request.scenarios, trigger_source="manual")
