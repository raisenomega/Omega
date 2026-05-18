"""
Reseller Detail Endpoint
GET /resellers/{reseller_id}/ - Full reseller profile with stats
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.resellers.handlers import handle_get_reseller_detail
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{reseller_id}/")
async def get_reseller_detail(
    reseller_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get full reseller detail including clients count and MRR"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_reseller_detail(reseller_id)
