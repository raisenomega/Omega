"""
Handler: Delete Post
Soft deletes (cancels) scheduled post
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.calendar.models import DeleteResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_delete_post(post_id: str) -> DeleteResponse:
    """
    Cancel (soft delete) scheduled post

    Args:
        post_id: Post UUID

    Returns:
        DeleteResponse confirmation

    Raises:
        HTTPException 404: Post not found
        HTTPException 400: Cannot delete post in current status
        HTTPException 500: Delete failed
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # 1. Find existing post
        post = await repo.find_by_id(post_id)
        if not post:
            raise HTTPException(404, f"Scheduled post {post_id} not found")

        # 2. Check if post can be deleted
        if not post.can_be_deleted():
            raise HTTPException(
                400,
                f"Cannot delete post with status '{post.status}'. "
                f"Post is currently being published."
            )

        # 3. Soft delete via repository
        success = await repo.delete(post_id)

        if not success:
            raise HTTPException(500, "Failed to delete post")

        logger.info(f"Deleted scheduled post {post_id}")

        # 4. Return confirmation
        return DeleteResponse(
            id=post_id,
            deleted=True,
            message="Scheduled post cancelled successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {e}")
        raise HTTPException(500, f"Failed to delete post: {str(e)}")
