"""Read operations mixin for ScheduledPostRepository"""
from typing import Optional, List
from datetime import date
import logging

from app.domain.calendar.entities import ScheduledPost

logger = logging.getLogger(__name__)


class ScheduledPostReadMixin:
    """Read-only operations: find, count, and entity mapping"""

    async def find_by_id(self, post_id: str) -> Optional[ScheduledPost]:
        """Find scheduled post by ID. Returns None if not found."""
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .select("*")\
                .eq("id", post_id)\
                .eq("is_active", True)\
                .execute()

            if not response.data:
                return None

            return self._map_to_entity(response.data[0])

        except Exception as e:
            logger.error(f"Error finding scheduled post {post_id}: {e}")
            return None

    async def find_by_account(
        self,
        account_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ScheduledPost]:
        """Find scheduled posts by account with pagination."""
        try:
            response = self.supabase.client.table("scheduled_posts")\
                .select("*")\
                .eq("account_id", account_id)\
                .eq("is_active", True)\
                .order("scheduled_date", desc=False)\
                .order("scheduled_time", desc=False)\
                .range(offset, offset + limit - 1)\
                .execute()

            if not response.data:
                return []

            return [self._map_to_entity(row) for row in response.data]

        except Exception as e:
            logger.error(f"Error finding posts for account {account_id}: {e}")
            return []

    async def count_by_date(self, account_id: str, scheduled_date: date) -> int:
        """Count active posts for account on specific date via RPC."""
        try:
            response = self.supabase.client.rpc(
                "count_posts_for_day",
                {
                    "p_account_id": account_id,
                    "p_date": str(scheduled_date),
                },
            ).execute()

            return response.data or 0

        except Exception as e:
            logger.error(f"Error counting posts: {e}")
            return 0

    def _map_to_entity(self, row: dict) -> ScheduledPost:
        """Map database row to ScheduledPost entity"""
        from datetime import datetime

        return ScheduledPost(
            id=row.get("id"),
            client_id=row.get("client_id"),
            account_id=row.get("account_id"),
            content_lab_id=row.get("content_lab_id"),
            content_type=row.get("content_type"),
            text_content=row.get("text_content"),
            image_url=row.get("image_url"),
            hashtags=row.get("hashtags", []),
            scheduled_date=(
                datetime.fromisoformat(row["scheduled_date"]).date()
                if row.get("scheduled_date") else None
            ),
            scheduled_time=(
                datetime.fromisoformat(f"2000-01-01T{row['scheduled_time']}").time()
                if row.get("scheduled_time") else None
            ),
            timezone=row.get("timezone", "America/Puerto_Rico"),
            status=row.get("status", "draft"),
            is_active=row.get("is_active", True),
            published_at=(
                datetime.fromisoformat(row["published_at"])
                if row.get("published_at") else None
            ),
            error_message=row.get("error_message"),
            created_at=(
                datetime.fromisoformat(row["created_at"])
                if row.get("created_at") else None
            ),
            updated_at=(
                datetime.fromisoformat(row["updated_at"])
                if row.get("updated_at") else None
            ),
        )
