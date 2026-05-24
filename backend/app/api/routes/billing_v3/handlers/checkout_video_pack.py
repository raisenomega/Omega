"""POST /api/v1/billing/checkout-video-pack · activate Video Pack addon (DEBT-VID-001).

3 packs spec §4.4: starter ($39 · 6×8s) · creator ($95 · 5×30s) ·
cinematic_pro ($125 · 3×60s). Solo basic/pro (Adopción rechazado).
Policy V1: 1 pack activo a la vez.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.billing_v3.models import (
    VideoPackCheckoutRequest, VideoPackCheckoutResponse,
)
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.bc_billing.application.create_video_pack_checkout import (
    create_video_pack_checkout,
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

_ERROR_CODE_TO_STATUS = {
    "invalid_video_pack_code": 400,
    "requires_paid_plan": 400,
    "already_active": 409,
    "client_not_found": 404,
    "client_plans_missing": 404,
    "price_not_configured": 503,
}


@router.post("/checkout-video-pack", response_model=VideoPackCheckoutResponse)
async def checkout_video_pack(
    request: VideoPackCheckoutRequest,
    authorization: Optional[str] = Header(None),
) -> VideoPackCheckoutResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    result = await create_video_pack_checkout(
        client_id=client_id,
        video_pack_code=request.video_pack_code,
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
    )
    if not result.get("success"):
        code = result.get("error_code") or "unknown"
        status = _ERROR_CODE_TO_STATUS.get(code, 500)
        logger.warning(f"video_pack_checkout failed · {code} · {result.get('error')}")
        raise HTTPException(status_code=status, detail=code)
    data = result.get("data") or {}
    return VideoPackCheckoutResponse(
        checkout_url=data["checkout_url"],
        session_id=data["session_id"],
    )
