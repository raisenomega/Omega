"""
Handler: Update Post
Updates existing scheduled post
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.calendar.models import ScheduledPostUpdate, ScheduledPostResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_update_post(
    post_id: str,
    request: ScheduledPostUpdate
) -> ScheduledPostResponse:
    """
    Update scheduled post

    Args:
        post_id: Post UUID
        request: ScheduledPostUpdate DTO with fields to update

    Returns:
        Updated ScheduledPostResponse

    Raises:
        HTTPException 404: Post not found
        HTTPException 400: Cannot edit post in current status
        HTTPException 500: Update failed
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # 1. Find existing post
        post = await repo.find_by_id(post_id)
        if not post:
            raise HTTPException(404, f"Scheduled post {post_id} not found")

        # 2. Check if post can be edited
        if not post.can_be_edited():
            raise HTTPException(
                400,
                f"Cannot edit post with status '{post.status}'. "
                f"Only draft, scheduled, or failed posts can be edited."
            )

        # 3. Apply updates (only non-None fields)
        if request.content_type is not None:
            post.content_type = request.content_type

        if request.text_content is not None:
            post.text_content = request.text_content

        if request.image_url is not None:
            post.image_url = request.image_url

        if request.hashtags is not None:
            post.hashtags = request.hashtags

        if request.scheduled_date is not None:
            post.scheduled_date = request.scheduled_date

        if request.scheduled_time is not None:
            post.scheduled_time = request.scheduled_time

        if request.timezone is not None:
            post.timezone = request.timezone

        if request.agent_assigned is not None:
            post.agent_assigned = request.agent_assigned

        # 4. Validate updated entity
        validation_errors = post.validate()
        if validation_errors:
            raise HTTPException(
                400,
                f"Validation errors: {', '.join(validation_errors)}"
            )

        # 5. Save via repository
        updated_post = await repo.update(post)

        logger.info(f"Updated scheduled post {post_id}")

        # 6. Map to response DTO
        return ScheduledPostResponse(
            id=updated_post.id,
            client_id=updated_post.client_id,
            account_id=updated_post.account_id,
            content_lab_id=updated_post.content_lab_id,
            content_type=updated_post.content_type,
            text_content=updated_post.text_content,
            image_url=updated_post.image_url,
            hashtags=updated_post.hashtags,
            scheduled_date=updated_post.scheduled_date,
            scheduled_time=updated_post.scheduled_time,
            timezone=updated_post.timezone,
            status=updated_post.status,
            agent_assigned=updated_post.agent_assigned,
            is_active=updated_post.is_active,
            created_at=updated_post.created_at.isoformat() if updated_post.created_at else "",
            updated_at=updated_post.updated_at.isoformat() if updated_post.updated_at else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {e}")
        raise HTTPException(500, f"Failed to update post: {str(e)}")
