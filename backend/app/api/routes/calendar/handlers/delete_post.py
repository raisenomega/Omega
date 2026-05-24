"""Handler: Delete Post · auth + RBAC obligatorios (G-capas).

Cierra agujero seguridad: ahora get_current_user + ownership check (vía
client_id del post) antes de soft delete.
"""
import logging
from typing import Optional
from fastapi import HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar.models import DeleteResponse
from app.api.routes.calendar._access import resolve_post_or_403
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_delete_post(
    post_id: str,
    authorization: Optional[str],
) -> DeleteResponse:
    user = await get_current_user(authorization)
    user_id = user["id"]
    supabase = get_supabase_service()
    repo = ScheduledPostRepository(supabase)

    resolve_post_or_403(supabase, post_id, user_id)  # ownership · raises 404/403

    post = await repo.find_by_id(post_id)
    if not post:
        raise HTTPException(404, "post_not_found")  # race condition
    if not post.can_be_deleted():
        raise HTTPException(400, f"cannot_delete_status:{post.status}")

    try:
        success = await repo.delete(post_id)
    except Exception as e:
        logger.error(f"delete_post failed · post={post_id} user={user_id}: {e}", exc_info=True)
        raise HTTPException(500, f"delete_failed:{type(e).__name__}")
    if not success:
        raise HTTPException(500, "delete_returned_false")

    logger.info(f"Deleted post {post_id} · user={user_id}")
    return DeleteResponse(id=post_id, deleted=True, message="Scheduled post cancelled successfully")
