"""POST /api/v1/aria/track · fire-and-forget behavioral event tracking.

Frontend dispara desde useBehavioralTracking hook. Backend siempre retorna
200 incluso si el INSERT falla (no bloquea UI cliente). Errors se loguean.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.aria_v1.models import ARIATrackRequest
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/track")
async def aria_track(
    request: ARIATrackRequest,
    authorization: Optional[str] = Header(None),
) -> dict:
    try:
        user = await get_current_user(authorization)
        supabase = get_supabase_service()
        client_row = supabase.client.table("clients").select("id").eq(
            "user_id", user["id"]
        ).limit(1).execute()
        if client_row.data:
            supabase.client.table("behavioral_events").insert({
                "user_id": user["id"], "client_id": client_row.data[0]["id"],
                "event_type": request.event_type, "event_data": request.event_data,
                "session_id": request.session_id,
            }).execute()
    except Exception as e:
        logger.warning(f"aria/track failed silently: {e}")
    return {"received": True}
