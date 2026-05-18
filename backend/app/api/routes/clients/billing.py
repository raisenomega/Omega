"""
Client Billing Endpoint
GET /clients/{client_id}/billing/ - Subscription and invoice data
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.clients.handlers import handle_get_client_billing
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{client_id}/billing/")
async def get_client_billing(
    client_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get billing information from Stripe or Supabase"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_client_billing(client_id)
