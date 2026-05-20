"""POST /billing/create-checkout-session · delega a bc_billing.application."""
import logging
from fastapi import APIRouter, HTTPException
from app.api.routes.billing_v3.models import CreateCheckoutRequest, CreateCheckoutResponse
from app.bc_billing.application.create_checkout import create_checkout_for_upgrade
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_target_plan": 400,
    "invalid_upgrade_path": 400,
    "client_not_found": 404,
    "price_not_configured": 503,
}


@router.post("/create-checkout-session", response_model=CreateCheckoutResponse)
async def create_checkout_session_endpoint(
    request: CreateCheckoutRequest,
) -> CreateCheckoutResponse:
    """Crea Stripe Checkout session para upgrade del cliente.

    Returns 200 con checkout_url si OK · maps error_code a HTTP status apropiado.
    """
    result = await create_checkout_for_upgrade(
        client_id=request.client_id,
        target_plan=request.target_plan,
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
    )

    if result.get("success"):
        data = result.get("data") or {}
        return CreateCheckoutResponse(
            success=True,
            checkout_url=data.get("checkout_url"),
            session_id=data.get("session_id"),
        )

    error_code = result.get("error_code") or "billing_error"
    error_msg = result.get("error") or "Unknown billing error"
    status = _ERROR_CODE_TO_STATUS.get(error_code, 500)
    logger.warning(f"Checkout failed · {error_code} · {error_msg}")
    raise HTTPException(status_code=status, detail={"error": error_msg, "error_code": error_code})
