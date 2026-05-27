"""POST /api/v1/billing/schedule-downgrade · programa downgrade a fin de ciclo (DEBT-076).

Auth + ownership obligatorios (operación consecuente · reduce el plan). Delega a
bc_billing.application.schedule_plan_downgrade (Stripe SubscriptionSchedule).
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.billing_v3.models import ScheduleDowngradeRequest, ScheduleDowngradeResponse
from app.bc_billing.application.schedule_downgrade import schedule_plan_downgrade

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_downgrade_path": 400,
    "no_active_subscription": 409,
    "client_not_found": 404,
    "price_not_configured": 503,
}


@router.post("/schedule-downgrade", response_model=ScheduleDowngradeResponse)
async def schedule_downgrade_endpoint(
    request: ScheduleDowngradeRequest,
    authorization: Optional[str] = Header(None),
) -> ScheduleDowngradeResponse:
    """Programa el downgrade del cliente al fin de su ciclo de facturación."""
    user = await get_current_user(authorization)
    client = reader.get_client(request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="access_denied")

    result = await schedule_plan_downgrade(request.client_id, request.target_plan)
    if result.get("success"):
        data = result.get("data") or {}
        return ScheduleDowngradeResponse(
            success=True, scheduled=True, target_plan=data.get("target_plan"),
        )

    error_code = result.get("error_code") or "billing_error"
    error_msg = result.get("error") or "Unknown billing error"
    status = _ERROR_CODE_TO_STATUS.get(error_code, 500)
    logger.warning(f"Schedule-downgrade failed · {error_code} · {error_msg}")
    raise HTTPException(status_code=status, detail={"error": error_msg, "error_code": error_code})
