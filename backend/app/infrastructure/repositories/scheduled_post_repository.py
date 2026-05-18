"""
Scheduled Post Repository
Data access layer for scheduled posts using Repository Pattern
Filosofía: No velocity, only precision 🐢💎
"""
import logging

from app.infrastructure.supabase_service import SupabaseService
from app.domain.calendar.entities import ScheduledPost
from ._scheduled_post_read_mixin import ScheduledPostReadMixin

logger = logging.getLogger(__name__)


class ScheduledPostRepository(ScheduledPostReadMixin):
    """Repository for scheduled posts data access"""

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create new scheduled post. Returns created entity with generated ID."""
        try:
            data = {
                "client_id": post.client_id,
                "account_id": post.account_id,
                "content_lab_id": post.content_lab_id,
                "content_type": post.content_type,
                "text_content": post.text_content,
                "image_url": post.image_url,
                "hashtags": post.hashtags or [],
                "scheduled_date": str(post.scheduled_date),
                "scheduled_time": str(post.scheduled_time),
                "timezone": post.timezone,
                "status": post.status,
                "is_active": post.is_active,
            }

            response = self.supabase.client.table("scheduled_posts")\
                .insert(data)\
                .execute()

            if not response.data:
                raise Exception("Failed to create scheduled post")

            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error creating scheduled post: {e}")
            raise

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update existing scheduled post. Returns updated entity."""
        try:
            data = {
                "content_type": post.content_type,
                "text_content": post.text_content,
                "image_url": post.image_url,
                "hashtags": post.hashtags or [],
                "scheduled_date": str(post.scheduled_date),
                "scheduled_time": str(post.scheduled_time),
                "timezone": post.timezone,
                "status": post.status,
                "error_message": post.error_message,
            }

            response = self.supabase.client.table("scheduled_posts")\
                .update(data)\
                .eq("id", post.id)\
                .execute()

            if not response.data:
                raise Exception("Failed to update scheduled post")

            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error updating scheduled post {post.id}: {e}")
            raise

    async def delete(self, post_id: str) -> bool:
        """Soft delete scheduled post (set is_active=False)."""
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .update({"is_active": False})\
                .eq("id", post_id)\
                .execute()

            return bool(response.data)

        except Exception as e:
            logger.error(f"Error deleting scheduled post {post_id}: {e}")
            raise
