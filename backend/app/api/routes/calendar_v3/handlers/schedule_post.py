"""POST /api/v1/calendar-v3/schedule/ · DEBT-CL-017 + DEBT-018 + DEBT-031 partial.

N text content_ids → N rows con timestamps espaciados según LIMITS_OMEGA
(_timestamp_spacer · 2h intra-día · 3 max/día). Atómico vía bulk insert
(repo · todos o ninguno). Auth + ownership obligatorios.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3 import _calendar_repository as repo, _calendar_reader as reader
from app.api.routes.calendar_v3 import _brand_voice_gate as brand_gate
from app.api.routes.calendar_v3._access import (
    resolve_client_or_403,
    resolve_account_by_client_platform_or_404,
    resolve_account_by_id_or_403,
)
from app.api.routes.calendar_v3._timestamp_spacer import space_timestamps
from app.api.routes.calendar_v3._fanout import build_fanout_rows
from app.api.routes.calendar_v3._schedule_response import to_responses
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
    n = len(request.content_ids)

    # Valida que los content_ids existan Y sean del client ANTES del insert · evita FK 500
    # opaco con ids stale del localStorage del frontend (P1: error honesto y accionable).
    existing = reader.fetch_existing_content_ids(request.client_id, request.content_ids)
    missing = [cid for cid in request.content_ids if cid not in existing]
    if missing:
        raise HTTPException(409, f"content_not_found:{','.join(missing)}")

    # X5 · gate brand voice (422 <0.7 · 503 con válvula force · override auditado ·
    # skipped=cliente sin voz de marca → PASS con rastro)
    bv = await brand_gate.check_or_raise(user_id, request.client_id, request.content_ids, request.force_brand_voice)

    timestamps = space_timestamps(request.scheduled_for, n)
    if request.platforms:
        # E · fan-out multi-red: N content_ids x M redes resueltas (primera active por red · omite sin-cuenta)
        rows_to_insert = build_fanout_rows(
            request.client_id, request.platforms, request.content_ids, timestamps, request.media_url)
        if not rows_to_insert:
            raise HTTPException(422, "no_account_for_any_platform")  # 0 redes resuelven · 0 rows basura
    else:
        # Legacy single-red · DEBT-CL-015: prioridad social_account_id (dropdown) → fallback primera activa
        if request.social_account_id:
            account = resolve_account_by_id_or_403(request.client_id, request.social_account_id)
        else:
            account = resolve_account_by_client_platform_or_404(request.client_id, request.platform)
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

    logger.info(f"V3 bulk_schedule {len(rows)} rows (n={n}) · user={user_id} · client={request.client_id} · platforms={request.platforms or request.platform}")
    return to_responses(rows, bv["skipped"], bv["below_brand_bar"])
