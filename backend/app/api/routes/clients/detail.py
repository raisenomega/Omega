"""
Client Detail Endpoint
GET /clients/{client_id}/ - Full client profile with reseller
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.clients.handlers import handle_get_client_detail
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{client_id}/")
async def get_client_detail(
    client_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get full client detail including reseller info"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_client_detail(client_id)
