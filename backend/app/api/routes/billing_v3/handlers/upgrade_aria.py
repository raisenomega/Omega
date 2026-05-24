"""POST /api/v1/billing/upgrade-aria · activate ARIA Premium client addon.

DEBT-037 V1 · solo client (reseller variant DEBT-046 futuro).
Retorna checkout_url para redirect del frontend (window.location).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_aria_premium_checkout import (
    create_aria_premium_checkout,
)
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
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    result = await create_aria_premium_checkout(
        client_id=client_id, addon_code="aria_premium_client",
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
    )
    # BONUS DEBT-VID-001 commit · fix bug latente: BillingResult es TypedDict
    # NO dataclass · acceso por keys (.get) en lugar de atributos (.ok/.error_code/.data)
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
