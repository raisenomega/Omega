"""POST /api/v1/calendar-v3/schedule/ · DEBT-CL-017 + DEBT-031 partial close.

Schema V3 correcto (vs calendar legacy que usa cols inexistentes):
  client_id, social_account_id, content_id, scheduled_for (timestamptz),
  status, media_url (nueva col migración 00020).

Resuelve social_account_id desde (client_id, platform) server-side (no
frontend query directo · DDD A1). Auth + ownership obligatorios.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3 import _calendar_repository as repo
from app.api.routes.calendar_v3._access import (
    resolve_client_or_403, resolve_account_by_client_platform_or_404,
)
from app.api.routes.calendar_v3.models.calendar_models import (
    ScheduledPostV3Create, ScheduledPostV3Response,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule/", response_model=ScheduledPostV3Response, status_code=201)
async def schedule_post_v3(
    request: ScheduledPostV3Create,
    authorization: Optional[str] = Header(None),
) -> ScheduledPostV3Response:
    user = await get_current_user(authorization)
    user_id = user["id"]
    resolve_client_or_403(user_id, request.client_id)
    account = resolve_account_by_client_platform_or_404(request.client_id, request.platform)
    try:
        row = repo.insert_scheduled_post(
            client_id=request.client_id,
            social_account_id=str(account["id"]),
            content_id=request.content_id,
            scheduled_for_iso=request.scheduled_for.isoformat(),
            media_url=request.media_url,
        )
    except Exception as e:
        logger.error(f"schedule_v3 failed · user={user_id} client={request.client_id}: {e}", exc_info=True)
        raise HTTPException(500, f"schedule_failed:{type(e).__name__}:{str(e)[:200]}")

    logger.info(f"V3 schedule_post {row.get('id')} · user={user_id} · client={request.client_id} · platform={request.platform}")
    return ScheduledPostV3Response(
        id=str(row["id"]),
        client_id=str(row["client_id"]),
        social_account_id=str(row.get("social_account_id") or "") or None,
        content_id=str(row.get("content_id") or "") or None,
        scheduled_for=str(row.get("scheduled_for") or ""),
        status=str(row.get("status") or "pending"),
        media_url=row.get("media_url"),
    )
