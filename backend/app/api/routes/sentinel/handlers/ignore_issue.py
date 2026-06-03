"""Handler: ignorar un issue de SENTINEL (registra en sentinel_issue_actions)."""
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.services.sentinel_helpers import issue_hash

logger = logging.getLogger(__name__)


class IssueActionRequest(BaseModel):
    agent_code: str
    severity: str
    type: str
    message: str
    scan_id: Optional[str] = None
    reason: Optional[str] = None
    source_type: str = "sentinel_scan"  # default retro-compat (filas existentes)
    source_id: Optional[str] = None     # apunta al scan/audit de la tabla origen


async def handle_ignore_issue(request: IssueActionRequest, authorization: Optional[str]) -> Dict[str, Any]:
    """Marca un issue como ignorado · owner-only. No oculta el issue en futuros scans."""
    await require_superadmin(authorization)
    h = issue_hash(request.severity, request.type, request.message)
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_issue_actions").insert({
        "scan_id": request.scan_id,
        "agent_code": request.agent_code,
        "issue_hash": h,
        "action": "ignored",
        "reason": request.reason,
        "source_type": request.source_type,
        "source_id": request.source_id,
    }).execute()
    action_id = (resp.data or [{}])[0].get("id")
    logger.info(f"sentinel issue ignored: {request.agent_code} {h[:12]}")
    return {"action_id": action_id, "issue_hash": h}
