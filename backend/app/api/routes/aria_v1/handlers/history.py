"""GET /api/v1/aria/history · HTTP layer · delega a use_aria_history.

DDD A1 + A9: handler solo importa de bc_cognition.application.
"""
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.aria_v1.models import ARIAHistoryResponse, ARIAConversationItem
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.application.use_aria_history import use_aria_history

router = APIRouter()


@router.get("/history", response_model=ARIAHistoryResponse)
async def aria_history(
    authorization: Optional[str] = Header(None),
) -> ARIAHistoryResponse:
    user = await get_current_user(authorization)
    rows = await use_aria_history(user_id=user["id"], limit=50)
    items = [
        ARIAConversationItem(
            role=r["role"],
            content=r["content"],
            aria_level=r.get("aria_level"),
            created_at=r["created_at"],
        )
        for r in rows
    ]
    return ARIAHistoryResponse(messages=items)
