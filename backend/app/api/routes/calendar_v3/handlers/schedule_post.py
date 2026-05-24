"""POST /api/v1/calendar-v3/schedule/ · DEBT-CL-017 + DEBT-018 + DEBT-031 partial.

N text content_ids → N rows con timestamps espaciados según LIMITS_OMEGA
(_timestamp_spacer · 2h intra-día · 3 max/día). Atómico vía bulk insert
(repo · todos o ninguno). Auth + ownership obligatorios.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3 import _calendar_repository as repo
from app.api.routes.calendar_v3._access import (
    resolve_client_or_403,
    resolve_account_by_client_platform_or_404,
    resolve_account_by_id_or_403,
)
from app.api.routes.calendar_v3._timestamp_spacer import space_timestamps
from app.api.routes.calendar_v3.models.calendar_models import (
    ScheduledPostV3Create, ScheduledPostV3Response,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/schedule/", response_model=list[ScheduledPostV3Response], status_code=201)
async def schedule_post_v3(
    request: ScheduledPostV3Create,
    authorization: Optional[str] = Header(None),
) -> list[ScheduledPostV3Response]:
    user = await get_current_user(authorization)
    user_id = user["id"]
    resolve_client_or_403(user_id, request.client_id)
    # DEBT-CL-015: prioridad social_account_id (user eligió en dropdown) → fallback primera activa
    if request.social_account_id:
        account = resolve_account_by_id_or_403(request.client_id, request.social_account_id)
    else:
        account = resolve_account_by_client_platform_or_404(request.client_id, request.platform)
    n = len(request.content_ids)

    timestamps = space_timestamps(request.scheduled_for, n)
    rows_to_insert = [
        {
            "client_id": request.client_id,
            "social_account_id": str(account["id"]),
            "content_id": cid,
            "scheduled_for": ts.isoformat(),
            "status": "pending",
            "media_url": request.media_url,
        }
        for cid, ts in zip(request.content_ids, timestamps)
    ]

    try:
        rows = repo.insert_scheduled_posts_bulk(rows_to_insert)
    except Exception as e:
        logger.error(f"schedule_bulk_v3 failed · user={user_id} client={request.client_id} n={n}: {e}", exc_info=True)
        raise HTTPException(500, f"schedule_bulk_failed:{type(e).__name__}:{str(e)[:200]}")

    logger.info(f"V3 bulk_schedule {n} rows · user={user_id} · client={request.client_id} · platform={request.platform}")
    return [
        ScheduledPostV3Response(
            id=str(r["id"]),
            client_id=str(r["client_id"]),
            social_account_id=str(r.get("social_account_id") or "") or None,
            content_id=str(r.get("content_id") or "") or None,
            scheduled_for=str(r.get("scheduled_for") or ""),
            status=str(r.get("status") or "pending"),
            media_url=r.get("media_url"),
        )
        for r in rows
    ]
