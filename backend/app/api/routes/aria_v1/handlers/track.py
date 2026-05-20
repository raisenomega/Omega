"""POST /api/v1/aria/track · HTTP layer · delega a use_aria_track.

Fire-and-forget · siempre retorna 200 (errors silenciados en use case).
DDD A1 + A9: handler solo importa de bc_cognition.application.
"""
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.aria_v1.models import ARIATrackRequest
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.application.use_aria_track import use_aria_track

router = APIRouter()


@router.post("/track")
async def aria_track(
    request: ARIATrackRequest,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    await use_aria_track(
        user_id=user["id"],
        event_type=request.event_type,
        event_data=request.event_data,
        session_id=request.session_id,
    )
    return {"received": True}
