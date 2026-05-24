"""Handler: Schedule Post · auth + RBAC obligatorios (G-capas).

DEPRECATED 23 may 2026 (Sprint 3 · DEBT-CL-017 path X):
  Schema usado aquí (account_id, image_url, text_content, scheduled_date,
  scheduled_time, hashtags, timezone, is_active, content_type, agent_assigned)
  NO matchea schema V3 real de scheduled_posts (DEBT-031). Cualquier insert
  contra DB V3 falla salvo que la DB legacy tenga esas cols paralelas.
  Frontend useScheduleBlock ahora apunta a /api/v1/calendar-v3/schedule/
  (handler V3 con schema correcto + media_url unificado).
  Mantener intacto temporalmente para back-compat con callers externos.
  Eliminar al cerrar DEBT-031 completa (refactor V3 full).

DEBT-CL-013 cerrada: si request.client_id+platform presente → backend
resuelve account_id internamente (frontend ya no query Supabase directo).
account_id legacy path preserved para back-compat.

Cierra agujero seguridad: cero auth previo · ahora get_current_user +
ownership check vía _access helpers antes de TODA escritura.
"""
import logging
from typing import Optional
from fastapi import HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar.models import ScheduledPostCreate, ScheduledPostResponse
from app.api.routes.calendar._access import (
    resolve_account_or_403, resolve_account_by_client_platform_or_404, resolve_client_or_403,
)
from app.domain.calendar.entities import ScheduledPost
from app.domain.calendar.config import get_daily_limit, can_schedule_more
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_schedule_post(
    request: ScheduledPostCreate,
    authorization: Optional[str],
) -> ScheduledPostResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]
    supabase = get_supabase_service()
    repo = ScheduledPostRepository(supabase)

    # DEBT-CL-013: resolver account_id desde account_id legacy O (client_id+platform) nuevo
    if request.account_id:
        account = resolve_account_or_403(supabase, request.account_id, user_id)
        account_id = str(account["id"])
        client_id = str(account["clients"]["id"])
        plan = account["clients"].get("plan") or "basico_97"
    elif request.client_id and request.platform:
        resolve_client_or_403(user_id, request.client_id)  # ownership check
        account = resolve_account_by_client_platform_or_404(
            supabase, request.client_id, request.platform,
        )
        account_id = str(account["id"])
        client_id = str(request.client_id)
        # plan: lookup desde client (legacy column · DEBT-031 no aplica acá)
        client_row = supabase.client.table("clients").select("plan").eq("id", client_id).execute()
        plan = (client_row.data[0].get("plan") if client_row.data else None) or "basico_97"
    else:
        raise HTTPException(400, "either account_id OR (client_id+platform) required")

    posts_today = await repo.count_by_date(account_id, request.scheduled_date)
    if not can_schedule_more(posts_today, plan):
        limit = get_daily_limit(plan)
        raise HTTPException(
            403,
            f"Daily limit reached. Plan {plan} allows {limit} posts/day. "
            f"You have {posts_today} scheduled for {request.scheduled_date}.",
        )

    post = ScheduledPost(
        client_id=client_id, account_id=account_id,
        content_lab_id=request.content_lab_id, content_type=request.content_type,
        text_content=request.text_content, image_url=request.image_url,
        hashtags=request.hashtags, scheduled_date=request.scheduled_date,
        scheduled_time=request.scheduled_time, timezone=request.timezone,
        status="scheduled", is_active=True,
    )
    errors = post.validate()
    if errors:
        raise HTTPException(400, f"Validation errors: {', '.join(errors)}")

    try:
        created = await repo.create(post)
    except Exception as e:
        logger.error(f"schedule_post create failed · user={user_id}: {e}", exc_info=True)
        raise HTTPException(500, f"schedule_failed:{type(e).__name__}")

    logger.info(f"Scheduled post {created.id} · user={user_id} · client={client_id} · account={account_id}")
    return ScheduledPostResponse(
        id=created.id, client_id=created.client_id, account_id=created.account_id,
        content_lab_id=created.content_lab_id, content_type=created.content_type,
        text_content=created.text_content, image_url=created.image_url,
        hashtags=created.hashtags, scheduled_date=created.scheduled_date,
        scheduled_time=created.scheduled_time, timezone=created.timezone,
        status=created.status, agent_assigned=created.agent_assigned,
        is_active=created.is_active,
        created_at=created.created_at.isoformat() if created.created_at else "",
        updated_at=created.updated_at.isoformat() if created.updated_at else "",
    )
