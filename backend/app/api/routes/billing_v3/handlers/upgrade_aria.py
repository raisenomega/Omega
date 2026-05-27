"""POST /api/v1/billing/upgrade-aria · activate ARIA Premium addon.

DEBT-037 V1 · client ($12/mes · aria_premium_client).
DEBT-046 · reseller ($25/mes · aria_premium_reseller).

Detects whether the authenticated user is a client or a reseller owner
and routes to the correct checkout use case. Retorna checkout_url.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_aria_premium_checkout import create_aria_premium_checkout
from app.bc_billing.application.reseller_aria import create_aria_premium_reseller_checkout
from app.bc_cognition.infrastructure.aria_repository import find_reseller_by_owner
from app.infrastructure.supabase_service import get_supabase_service
from app.config import settings

router = APIRouter()


class UpgradeAriaResponse(BaseModel):
    checkout_url: str
    session_id: str


@router.post("/upgrade-aria", response_model=UpgradeAriaResponse)
async def upgrade_aria(
    authorization: Optional[str] = Header(None),
) -> UpgradeAriaResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]

    # DEBT-046: detect reseller first (owner_user_id lookup); fall through to client.
    supabase = get_supabase_service()
    reseller = find_reseller_by_owner(supabase, user_id)
    if reseller:
        result = await create_aria_premium_reseller_checkout(
            reseller_id=str(reseller["id"]), addon_code="aria_premium_reseller",
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
        )
    else:
        client = repo.find_client_for_user(user_id)
        if not client:
            raise HTTPException(status_code=403, detail="no_client_or_reseller_for_user")
        result = await create_aria_premium_checkout(
            client_id=str(client["id"]), addon_code="aria_premium_client",
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
        )

    # BillingResult es TypedDict · acceso por keys (.get) en lugar de atributos.
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        status = (
            409 if code == "already_active"
            else 503 if code == "price_not_configured"
            else 400
        )
        raise HTTPException(status_code=status, detail=code)
    data = result.get("data") or {}
    return UpgradeAriaResponse(
        checkout_url=data["checkout_url"],
        session_id=data["session_id"],
    )
