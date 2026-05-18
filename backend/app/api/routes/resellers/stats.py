"""
Reseller Stats Endpoint
GET /resellers/{reseller_id}/stats/ - Performance metrics
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.resellers.handlers import handle_get_reseller_stats
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{reseller_id}/stats/")
async def get_reseller_stats(
    reseller_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get performance metrics for this reseller"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_reseller_stats(reseller_id)
