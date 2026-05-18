"""
Reseller Clients Endpoint
GET /resellers/{reseller_id}/clients/ - List clients for reseller
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.resellers.handlers import handle_get_reseller_clients
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{reseller_id}/clients/")
async def get_reseller_clients(
    reseller_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get list of clients for this reseller"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_reseller_clients(reseller_id)
