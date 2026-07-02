"""Notificaciones in-app del usuario ACTUAL (get_current_user · cada quien las suyas). El backend
inserta con service-role desde el flujo de leads (notify) · aquí solo se listan y marcan leídas."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Header

from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications 🔔"])
logger = logging.getLogger(__name__)


@router.get("", response_model=APIResponse)
async def list_notifications(authorization: Optional[str] = Header(None)) -> APIResponse:
    """Las notificaciones del usuario actual (recientes primero) · 401 sin token."""
    user = await get_current_user(authorization)
    service = get_supabase_service()
    items = await service.get_notifications(user["id"])
    unread = sum(1 for n in items if not n.get("is_read"))
    return APIResponse(success=True, data={"notifications": items, "unread": unread}, message=f"{len(items)} notifications")


@router.patch("/{notification_id}/read", response_model=APIResponse)
async def mark_read(notification_id: str, authorization: Optional[str] = Header(None)) -> APIResponse:
    """Marca leída SOLO si es del usuario actual (scope server-side · 401 sin token)."""
    try:
        user = await get_current_user(authorization)
        service = get_supabase_service()
        await service.mark_notification_read(notification_id, user["id"])
        return APIResponse(success=True, data={}, message="Marked read")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification read: {e}")
        raise HTTPException(status_code=500, detail=str(e))
