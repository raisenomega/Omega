"""
Reseller Billing Endpoint
GET /resellers/{reseller_id}/billing/ - Subscription and commission data
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.resellers.handlers import handle_get_reseller_billing
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{reseller_id}/billing/")
async def get_reseller_billing(
    reseller_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get billing information from Stripe or Supabase"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_reseller_billing(reseller_id)
