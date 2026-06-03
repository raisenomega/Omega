"""Handler: despachar Fix de un issue SENTINEL → registra + devuelve prompt para Dev Chat.

NO ejecuta nada (DEV-R2): solo registra la acción y arma el prompt que el operador
copiará en Claude DEV Chat (placeholder hasta Sprint 8 · DEBT-106).
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.services.sentinel_helpers import issue_hash

logger = logging.getLogger(__name__)


class DispatchFixRequest(BaseModel):
    agent_code: str
    severity: str
    type: str
    message: str
    scan_id: Optional[str] = None
    reason: Optional[str] = None
    source_type: str = "sentinel_scan"      # default retro-compat
    source_id: Optional[str] = None         # scan/audit de la tabla origen
    dispatch_prompt: Optional[str] = None   # prompt ya formateado por el frontend (single source)


async def handle_dispatch_fix(request: DispatchFixRequest, authorization: Optional[str]) -> Dict[str, Any]:
    """Registra fix_dispatched + devuelve dispatch_prompt para precargar en Dev Chat.

    El prompt lo arma el frontend (sentinel_fix_prompt_builders · single source). Si no llega,
    fallback retro-compat para el path legacy sentinel_scan.
    """
    await require_superadmin(authorization)
    h = issue_hash(request.severity, request.type, request.message)
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_issue_actions").insert({
        "scan_id": request.scan_id,
        "agent_code": request.agent_code,
        "issue_hash": h,
        "action": "fix_dispatched",
        "reason": request.reason,
        "source_type": request.source_type,
        "source_id": request.source_id,
    }).execute()
    action_id = (resp.data or [{}])[0].get("id")
    dispatch_prompt = request.dispatch_prompt or (
        f"Fix needed: agent={request.agent_code}, severity={request.severity}, "
        f"type={request.type}, message={request.message}, scan_id={request.scan_id or 'n/a'}"
    )
    logger.info(f"sentinel fix dispatched: {request.source_type}/{request.agent_code} {h[:12]}")
    return {"action_id": action_id, "issue_hash": h, "dispatch_prompt": dispatch_prompt}
