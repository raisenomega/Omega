"""POST /api/v1/aria/message · HTTP layer · delega a application use case.

DDD A1 + A9: handler solo importa de bc_cognition.application.
Cero imports de infrastructure (Supabase, anthropic_adapter).
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.api.routes.aria_v1.models import ARIAMessageRequest, ARIAMessageResponse
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_cognition.application.use_aria_message import use_aria_message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ARIAMessageResponse)
async def aria_message(
    request: ARIAMessageRequest,
    authorization: Optional[str] = Header(None),
) -> ARIAMessageResponse:
    user = await get_current_user(authorization)
    # Switcher V1: resolver+validar el negocio activo acá (A2: el use case no toca api.routes).
    # Ausente → use case cae a resolve_role legacy. resolve_client_or_403 lanza 404/403.
    client_id: Optional[str] = None
    level: Optional[int] = None
    if request.client_id:
        client = resolve_client_or_403(user["id"], request.client_id)
        client_id = str(client["id"])
        level = client.get("aria_level") or 1
    result, err = await use_aria_message(
        user_id=user["id"], user_message=request.content,
        client_id=client_id, level=level,
    )
    if err or not result:
        status = 403 if err and err.code == "forbidden" else 503
        msg = err.message if err else "ARIA no disponible"
        logger.warning(f"ARIA message failed · {status} · {msg}")
        raise HTTPException(status_code=status, detail=msg)
    return ARIAMessageResponse(content=result.content, aria_level=result.aria_level)
