"""POST /api/v1/billing/admin/credits/{transfer,release} · superadmin (DEBT-052 FASE 4).

Mover/liberar créditos entre clientes. Gateado con require_superadmin (role==owner ·
derivado server-side · forgery-proof). Delega a bc_billing.application.admin_credit_ops.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import require_superadmin
from app.api.routes.billing_v3.models import (
    TransferCreditsRequest, ReleaseCreditsRequest, AdminCreditsResponse,
)
from app.bc_billing.application.admin_credit_ops import transfer_credits, release_credits

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_amount": 400, "same_client": 400,
    "not_enrolled": 404, "insufficient_budget": 409, "infra_error": 500,
}


def _respond(result: dict) -> AdminCreditsResponse:
    if result.get("success"):
        return AdminCreditsResponse(success=True, data=result.get("data") or {})
    code = result.get("error_code") or "billing_error"
    status = _ERROR_CODE_TO_STATUS.get(code, 500)
    logger.warning(f"admin_credits op failed · {code} · {result.get('error')}")
    raise HTTPException(status_code=status, detail={"error": result.get("error"), "error_code": code})


@router.post("/admin/credits/transfer", response_model=AdminCreditsResponse)
async def admin_transfer_credits(
    request: TransferCreditsRequest, authorization: Optional[str] = Header(None),
) -> AdminCreditsResponse:
    await require_superadmin(authorization)
    return _respond(await transfer_credits(request.from_client_id, request.to_client_id, request.amount_usd))


@router.post("/admin/credits/release", response_model=AdminCreditsResponse)
async def admin_release_credits(
    request: ReleaseCreditsRequest, authorization: Optional[str] = Header(None),
) -> AdminCreditsResponse:
    await require_superadmin(authorization)
    return _respond(await release_credits(request.client_id, request.amount_usd))
