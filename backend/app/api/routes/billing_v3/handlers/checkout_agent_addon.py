"""POST /api/v1/billing/checkout-agent-addon · activar un Agent Add-On (DEBT-091).

5 agentes (recurring monthly · /add-ons): publisher_esencial/pro · creative_esencial/pro
· trends_unico. Requiere plan pago. Permite varios agentes, no el mismo dos veces.
El alta (client_plans.addons) la hace el webhook → _agent_addon_handlers. Auth cliente.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.billing_v3.models import (
    AgentAddonCheckoutRequest, AgentAddonCheckoutResponse,
)
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_agent_addon_checkout import (
    create_agent_addon_checkout,
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_agent_addon_code": 400,
    "requires_paid_plan": 400,
    "already_active": 409,
    "client_not_found": 404,
    "client_plans_missing": 404,
    "price_not_configured": 503,
}


@router.post("/checkout-agent-addon", response_model=AgentAddonCheckoutResponse)
async def checkout_agent_addon(
    request: AgentAddonCheckoutRequest,
    authorization: Optional[str] = Header(None),
) -> AgentAddonCheckoutResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    result = await create_agent_addon_checkout(
        client_id=client_id,
        agent_addon_code=request.agent_addon_code,
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
    )
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        status = _ERROR_CODE_TO_STATUS.get(code, 500)
        logger.warning(f"agent_addon_checkout failed · {code} · {result.get('error')}")
        raise HTTPException(status_code=status, detail=code)
    data = result.get("data") or {}
    return AgentAddonCheckoutResponse(
        checkout_url=data["checkout_url"],
        session_id=data["session_id"],
    )
