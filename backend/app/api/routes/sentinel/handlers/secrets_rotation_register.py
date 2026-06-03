"""Handler: registrar una rotación manual de secret · owner-only.

Solo recibe el NOMBRE del secret + nota opcional · NUNCA el valor. Inserta el timestamp.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.workers.sentinel_secrets_monitor import SECRETS_ROTATION_POLICY

logger = logging.getLogger(__name__)


class RegisterRotationRequest(BaseModel):
    secret_name: str
    note: Optional[str] = None


async def handle_register_rotation(request: RegisterRotationRequest, authorization: Optional[str]) -> Dict[str, Any]:
    """Registra rotación (rotated_at=now · rotated_by=user.id). Valida contra lista cerrada."""
    user = await require_superadmin(authorization)
    if request.secret_name not in SECRETS_ROTATION_POLICY:
        raise HTTPException(status_code=400, detail=f"secret_name desconocido: {request.secret_name}")
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_secrets_log").insert({
        "secret_name": request.secret_name,
        "rotated_at": datetime.now(timezone.utc).isoformat(),
        "rotated_by": user.get("id"),
        "note": request.note or "manual_rotation",
    }).execute()
    row = (resp.data or [{}])[0]
    logger.info(f"secret rotation registered: {request.secret_name} by {user.get('id')}")
    return {"success": True, "rotation_id": row.get("id"), "secret_name": request.secret_name,
            "rotated_at": row.get("rotated_at")}
