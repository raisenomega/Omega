"""
Reseller Activity Endpoint
GET /resellers/{reseller_id}/activity/ - Activity feed
"""
from fastapi import APIRouter, Header, Query
from typing import Optional
from app.api.routes.resellers.handlers import handle_get_reseller_activity
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{reseller_id}/activity/")
async def get_reseller_activity(
    reseller_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    authorization: Optional[str] = Header(None)
):
    """Get recent activity for this reseller"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_reseller_activity(reseller_id, limit, offset)
