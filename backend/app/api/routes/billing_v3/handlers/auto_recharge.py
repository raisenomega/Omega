"""POST /api/v1/billing/credits/auto-recharge · toggle auto-recarga (DEBT-052 FASE 4).

El cliente activa/desactiva la auto-recarga de su credit pack (storage en packs jsonb).
Cuando está ON y el saldo cae a ≤20%, el débito dispara maybe_auto_recharge (cobro
off-session Stripe · 503 honesto si no configurado). Auth cliente (client_id del user).
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.billing_v3.models import AutoRechargeRequest, AutoRechargeResponse
from app.bc_billing.application.auto_recharge_service import set_auto_recharge

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {"not_enrolled": 404, "no_active_pack": 409, "infra_error": 503}


@router.post("/credits/auto-recharge", response_model=AutoRechargeResponse)
async def toggle_auto_recharge(
    request: AutoRechargeRequest, authorization: Optional[str] = Header(None),
) -> AutoRechargeResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    result = await set_auto_recharge(str(client["id"]), request.enabled)
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        logger.warning(f"auto_recharge toggle failed · {code}")
        raise HTTPException(status_code=_ERROR_CODE_TO_STATUS.get(code, 500), detail=code)
    return AutoRechargeResponse(success=True, auto_recharge=request.enabled)
