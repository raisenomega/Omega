"""Handler: Update Post · auth + RBAC obligatorios (G-capas).

Cierra agujero seguridad: ahora get_current_user + ownership check (vía
client_id del post) antes de cualquier mutación.
"""
import logging
from typing import Optional
from fastapi import HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar.models import ScheduledPostUpdate, ScheduledPostResponse
from app.api.routes.calendar._access import resolve_post_or_403
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_update_post(
    post_id: str,
    request: ScheduledPostUpdate,
    authorization: Optional[str],
) -> ScheduledPostResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]
    supabase = get_supabase_service()
    repo = ScheduledPostRepository(supabase)

    resolve_post_or_403(supabase, post_id, user_id)  # ownership · raises 404/403

    post = await repo.find_by_id(post_id)
    if not post:
        raise HTTPException(404, "post_not_found")  # race condition (deleted between checks)
    if not post.can_be_edited():
        raise HTTPException(400, f"cannot_edit_status:{post.status}")

    if request.content_type is not None: post.content_type = request.content_type
    if request.text_content is not None: post.text_content = request.text_content
    if request.image_url is not None: post.image_url = request.image_url
    if request.hashtags is not None: post.hashtags = request.hashtags
    if request.scheduled_date is not None: post.scheduled_date = request.scheduled_date
    if request.scheduled_time is not None: post.scheduled_time = request.scheduled_time
    if request.timezone is not None: post.timezone = request.timezone
    if request.agent_assigned is not None: post.agent_assigned = request.agent_assigned

    errors = post.validate()
    if errors:
        raise HTTPException(400, f"validation_errors:{','.join(errors)}")
    try:
        updated = await repo.update(post)
    except Exception as e:
        logger.error(f"update_post failed · post={post_id} user={user_id}: {e}", exc_info=True)
        raise HTTPException(500, f"update_failed:{type(e).__name__}")

    logger.info(f"Updated post {post_id} · user={user_id}")
    return ScheduledPostResponse(
        id=updated.id, client_id=updated.client_id, account_id=updated.account_id,
        content_lab_id=updated.content_lab_id, content_type=updated.content_type,
        text_content=updated.text_content, image_url=updated.image_url,
        hashtags=updated.hashtags, scheduled_date=updated.scheduled_date,
        scheduled_time=updated.scheduled_time, timezone=updated.timezone,
        status=updated.status, agent_assigned=updated.agent_assigned,
        is_active=updated.is_active,
        created_at=updated.created_at.isoformat() if updated.created_at else "",
        updated_at=updated.updated_at.isoformat() if updated.updated_at else "",
    )
