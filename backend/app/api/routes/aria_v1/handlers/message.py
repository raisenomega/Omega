"""POST /api/v1/aria/message · HTTP layer · delega a application use case.

DDD A1 + A9: handler solo importa de bc_cognition.application.
Cero imports de infrastructure (Supabase, anthropic_adapter).
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.api.routes.aria_v1.models import ARIAMessageRequest, ARIAMessageResponse
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.application.use_aria_message import use_aria_message

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/message", response_model=ARIAMessageResponse)
async def aria_message(
    request: ARIAMessageRequest,
    authorization: Optional[str] = Header(None),
) -> ARIAMessageResponse:
    user = await get_current_user(authorization)
    result, err = await use_aria_message(
        user_id=user["id"], user_message=request.content,
    )
    if err or not result:
        status = 403 if err and err.code == "forbidden" else 503
        msg = err.message if err else "ARIA no disponible"
        logger.warning(f"ARIA message failed · {status} · {msg}")
        raise HTTPException(status_code=status, detail=msg)
    return ARIAMessageResponse(content=result.content, aria_level=result.aria_level)
