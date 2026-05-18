"""
Handler: List Posts
Retrieves scheduled posts for an account
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.calendar.models import ScheduledPostListResponse, ScheduledPostResponse
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_list_posts(
    account_id: str = None,
    client_id: str = None,
    user_id: str = None,
    limit: int = 20,
    offset: int = 0,
    status: str = None
) -> ScheduledPostListResponse:
    """
    List scheduled posts for an account, client, or user

    Args:
        account_id: Social account UUID
        client_id: Client UUID
        user_id: User UUID (auto-discovers all clients owned by user)
        limit: Max results per page
        offset: Pagination offset
        status: Optional status filter (draft, scheduled, published, etc.)

    Returns:
        ScheduledPostListResponse with paginated results

    Raises:
        HTTPException 400: If no ID provided
        HTTPException 404: If user_id has no clients
        HTTPException 500: If query fails
    """
    try:
        # Validate: at least one ID must be provided
        if not account_id and not client_id and not user_id:
            raise HTTPException(
                400,
                "Either account_id, client_id, or user_id must be provided"
            )

        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # If user_id provided, find all their clients first
        client_ids = []
        if user_id:
            clients_response = supabase.client.table("clients")\
                .select("id")\
                .eq("user_id", user_id)\
                .eq("is_active", True)\
                .execute()

            if not clients_response.data:
                raise HTTPException(
                    404,
                    f"No active clients found for user {user_id}"
                )

            client_ids = [c["id"] for c in clients_response.data]
            logger.info(f"Found {len(client_ids)} clients for user {user_id}")

        # Build base query
        query = supabase.client.table("scheduled_posts")\
            .select("*")\
            .eq("is_active", True)

        # Filter by account_id, client_id, OR client_ids (from user_id)
        if account_id:
            query = query.eq("account_id", account_id)
        elif client_id:
            query = query.eq("client_id", client_id)
        elif client_ids:
            query = query.in_("client_id", client_ids)

        # Add status filter if provided
        if status:
            query = query.eq("status", status)

        # Order and paginate
        query = query.order("scheduled_date", desc=False)\
            .order("scheduled_time", desc=False)\
            .range(offset, offset + limit - 1)

        # Execute query
        response = query.execute()
        posts = [repo._map_to_entity(row) for row in response.data]

        # Count total (for pagination)
        count_query = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("is_active", True)

        if account_id:
            count_query = count_query.eq("account_id", account_id)
        elif client_id:
            count_query = count_query.eq("client_id", client_id)
        elif client_ids:
            count_query = count_query.in_("client_id", client_ids)

        if status:
            count_query = count_query.eq("status", status)

        count_response = count_query.execute()

        total = count_response.count if hasattr(count_response, 'count') else len(posts)

        # Map to response DTOs
        items = [
            ScheduledPostResponse(
                id=post.id,
                client_id=post.client_id,
                account_id=post.account_id,
                content_lab_id=post.content_lab_id,
                content_type=post.content_type,
                text_content=post.text_content,
                image_url=post.image_url,
                hashtags=post.hashtags,
                scheduled_date=post.scheduled_date,
                scheduled_time=post.scheduled_time,
                timezone=post.timezone,
                status=post.status,
                agent_assigned=post.agent_assigned,
                is_active=post.is_active,
                created_at=post.created_at.isoformat() if post.created_at else "",
                updated_at=post.updated_at.isoformat() if post.updated_at else "",
            )
            for post in posts
        ]

        logger.info(f"Listed {len(items)} posts for account {account_id}")

        return ScheduledPostListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error listing posts for account {account_id}: {e}")
        raise HTTPException(500, f"Failed to list posts: {str(e)}")
