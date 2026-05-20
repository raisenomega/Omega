"""GET /api/v1/aria/history · últimos 50 mensajes ASC del usuario autenticado."""
import logging
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.aria_v1.models import ARIAHistoryResponse, ARIAConversationItem
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/history", response_model=ARIAHistoryResponse)
async def aria_history(
    authorization: Optional[str] = Header(None),
) -> ARIAHistoryResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    resp = supabase.client.table("aria_conversations").select(
        "role, content, aria_level, created_at"
    ).eq("user_id", user["id"]).order("created_at", desc=False).limit(50).execute()

    items = [
        ARIAConversationItem(
            role=r["role"],
            content=r["content"],
            aria_level=r.get("aria_level"),
            created_at=r["created_at"],
        )
        for r in (resp.data or [])
    ]
    return ARIAHistoryResponse(messages=items)
