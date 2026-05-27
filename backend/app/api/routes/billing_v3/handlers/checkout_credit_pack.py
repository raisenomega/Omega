"""POST /api/v1/billing/checkout-credit-pack · comprar Credit Pack (DEBT-052 FASE 4).

4 packs (budget mensual prepagado de API · texto/imagen): micro $9 / starter $25
/ plus $59 / ultra $119. Requiere plan pago. Policy V1: 1 pack activo a la vez.
El enrolamiento (fila client_agent_credits) lo hace el webhook → _credit_pack_handlers.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.billing_v3.models import (
    CreditPackCheckoutRequest, CreditPackCheckoutResponse,
)
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_credit_pack_checkout import (
    create_credit_pack_checkout,
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_credit_pack_code": 400,
    "requires_paid_plan": 400,
    "already_active": 409,
    "client_not_found": 404,
    "price_not_configured": 503,
}


@router.post("/checkout-credit-pack", response_model=CreditPackCheckoutResponse)
async def checkout_credit_pack(
    request: CreditPackCheckoutRequest,
    authorization: Optional[str] = Header(None),
) -> CreditPackCheckoutResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    result = await create_credit_pack_checkout(
        client_id=client_id,
        credit_pack_code=request.credit_pack_code,
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
    )
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        status = _ERROR_CODE_TO_STATUS.get(code, 500)
        logger.warning(f"credit_pack_checkout failed · {code} · {result.get('error')}")
        raise HTTPException(status_code=status, detail=code)
    data = result.get("data") or {}
    return CreditPackCheckoutResponse(
        checkout_url=data["checkout_url"],
        session_id=data["session_id"],
    )
