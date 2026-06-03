"""Handler: disparar auditoría RLS inline (botón "Auditar ahora") · owner-only."""
from typing import Dict, Any, Optional

from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_rls_worker import run_rls_audit_scan


async def handle_rls_audit_trigger(authorization: Optional[str]) -> Dict[str, Any]:
    """Corre la auditoría ahora mismo y devuelve el resultado inmediato."""
    await require_superadmin(authorization)
    return await run_rls_audit_scan()
