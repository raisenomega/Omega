"""POST /api/v1/billing/customer-portal · Stripe Customer Portal session (DEBT-038).

El cliente gestiona su suscripción (método de pago, cancelar, ver facturas) en
el portal hosteado de Stripe. Sin request body · el cliente sale del JWT.
503 honesto si Stripe no está configurado · 409 si aún no hay stripe_customer_id.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.billing_v3.models import CustomerPortalResponse
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_customer_portal import create_customer_portal
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "no_stripe_customer": 409,
    "client_not_found": 404,
    "stripe_not_configured": 503,
}


@router.post("/customer-portal", response_model=CustomerPortalResponse)
async def customer_portal(
    authorization: Optional[str] = Header(None),
) -> CustomerPortalResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    result = await create_customer_portal(
        client_id=client_id, return_url=settings.stripe_success_url,
    )
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        status = _ERROR_CODE_TO_STATUS.get(code, 500)
        logger.warning(f"customer_portal failed · {code} · {result.get('error')}")
        raise HTTPException(status_code=status, detail=code)
    data = result.get("data") or {}
    return CustomerPortalResponse(portal_url=data["portal_url"])
