"""
Calendar Repository - Saves scheduled posts to Supabase.
DDD: Infrastructure layer - Database persistence.
Max 200L strict. Type-safe.
"""
from typing import List, Dict, Any
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class CalendarRepository:
    """
    Repository for managing scheduled posts in Supabase.

    Table: scheduled_posts
    """

    def __init__(self) -> None:
        """Initialize Supabase client with service role key."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set"
            )

        self.client: Client = create_client(supabase_url, supabase_key)

    async def save_scheduled_posts(
        self,
        posts: List[Dict[str, Any]],
        client_id: str
    ) -> Dict[str, Any]:
        """
        Insert scheduled posts into Supabase.

        Args:
            posts: List of post dicts with all required fields
            client_id: Client UUID (used as fallback if not in posts)

        Returns:
            Dict with results:
            {
                "inserted": int,
                "failed": int,
                "ids": list[str]
            }

        Raises:
            Exception: If Supabase insert fails
        """
        if not posts:
            logger.warning("No posts to save")
            return {"inserted": 0, "failed": 0, "ids": []}

        # Ensure all posts have client_id and account_id
        for post in posts:
            if "client_id" not in post or not post["client_id"]:
                post["client_id"] = client_id
            # Add account_id (Instagram account for Milagrosa) if missing
            post["account_id"] = post.get("account_id", "cb1dfe0a-43a2-4e9b-9099-df6035f76700")

        inserted = 0
        failed = 0
        ids = []

        for post in posts:
            try:
                # Insert post
                response = self.client.table("scheduled_posts")\
                    .insert(post)\
                    .execute()

                if response.data:
                    inserted += 1
                    post_id = response.data[0].get("id", "unknown")
                    ids.append(post_id)
                    logger.info(
                        f"Saved post: {post['text_content'][:30]}... "
                        f"on {post['scheduled_date']} (ID: {post_id})"
                    )
                else:
                    failed += 1
                    logger.error(f"Failed to save post: {post['text_content'][:30]}")

            except Exception as e:
                failed += 1
                logger.error(
                    f"Error saving post '{post['text_content'][:30]}...': {e}",
                    exc_info=True
                )

        logger.info(
            f"Batch save complete: {inserted} inserted, {failed} failed"
        )

        return {
            "inserted": inserted,
            "failed": failed,
            "ids": ids
        }

    async def get_scheduled_posts(
        self,
        client_id: str,
        status: str = "scheduled"
    ) -> List[Dict[str, Any]]:
        """
        Get scheduled posts for a client.

        Args:
            client_id: Client UUID
            status: Post status filter (default: "scheduled")

        Returns:
            List of post dicts

        Raises:
            Exception: If Supabase query fails
        """
        try:
            query = self.client.table("scheduled_posts")\
                .select("*")\
                .eq("client_id", client_id)\
                .eq("is_active", True)

            if status:
                query = query.eq("status", status)

            response = query.order("scheduled_date, scheduled_time").execute()

            if response.data:
                logger.info(
                    f"Retrieved {len(response.data)} scheduled posts "
                    f"for client {client_id}"
                )
                return response.data
            else:
                logger.info(f"No scheduled posts found for client {client_id}")
                return []

        except Exception as e:
            logger.error(
                f"Error retrieving scheduled posts for client {client_id}: {e}",
                exc_info=True
            )
            raise

    async def update_post_status(
        self,
        post_id: str,
        status: str
    ) -> bool:
        """
        Update the status of a scheduled post.

        Args:
            post_id: Post UUID
            status: New status (scheduled, published, failed, etc.)

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            response = self.client.table("scheduled_posts")\
                .update({"status": status})\
                .eq("id", post_id)\
                .execute()

            if response.data:
                logger.info(f"Updated post {post_id} status to '{status}'")
                return True
            else:
                logger.warning(f"Failed to update post {post_id}")
                return False

        except Exception as e:
            logger.error(
                f"Error updating post {post_id} status: {e}",
                exc_info=True
            )
            return False
