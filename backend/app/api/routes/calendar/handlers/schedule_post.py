"""
Handler: Schedule Post
Creates new scheduled post with plan limit validation
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import HTTPException
import logging

from app.api.routes.calendar.models import ScheduledPostCreate, ScheduledPostResponse
from app.domain.calendar.entities import ScheduledPost
from app.domain.calendar.config import get_daily_limit, can_schedule_more
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def handle_schedule_post(request: ScheduledPostCreate) -> ScheduledPostResponse:
    """
    Schedule a new post with plan limit validation

    Workflow:
    1. Get account and client plan from DB
    2. Count existing posts for the day
    3. Validate against plan limits
    4. Create ScheduledPost entity
    5. Validate business rules
    6. Save to DB via repository
    7. Return response DTO

    Args:
        request: ScheduledPostCreate DTO

    Returns:
        ScheduledPostResponse DTO

    Raises:
        HTTPException 403: Daily limit reached
        HTTPException 404: Account not found
        HTTPException 400: Validation errors
    """
    try:
        # Get services
        supabase = get_supabase_service()
        repo = ScheduledPostRepository(supabase)

        # 1. Get account with client info
        account_response = supabase.client.table("social_accounts")\
            .select("*, clients!inner(id, plan)")\
            .eq("id", request.account_id)\
            .execute()

        if not account_response.data:
            raise HTTPException(404, "Social account not found")

        account = account_response.data[0]
        client_id = account["clients"]["id"]
        plan = account["clients"]["plan"] or "basico_97"

        # 2. Count posts for the day
        posts_today = await repo.count_by_date(
            request.account_id,
            request.scheduled_date
        )

        # 3. Validate plan limits
        if not can_schedule_more(posts_today, plan):
            limit = get_daily_limit(plan)
            raise HTTPException(
                403,
                f"Daily limit reached. Plan {plan} allows {limit} posts per day. "
                f"You have {posts_today} posts scheduled for {request.scheduled_date}."
            )

        # 4. Create entity
        post = ScheduledPost(
            client_id=client_id,
            account_id=request.account_id,
            content_lab_id=request.content_lab_id,
            content_type=request.content_type,
            text_content=request.text_content,
            image_url=request.image_url,
            hashtags=request.hashtags,
            scheduled_date=request.scheduled_date,
            scheduled_time=request.scheduled_time,
            timezone=request.timezone,
            status="scheduled",
            is_active=True,
        )

        # 5. Validate business rules
        validation_errors = post.validate()
        if validation_errors:
            raise HTTPException(400, f"Validation errors: {', '.join(validation_errors)}")

        # 6. Save via repository
        created_post = await repo.create(post)

        logger.info(
            f"Scheduled post created: {created_post.id} for account {request.account_id} "
            f"on {request.scheduled_date} at {request.scheduled_time}"
        )

        # 7. Map to response DTO
        return ScheduledPostResponse(
            id=created_post.id,
            client_id=created_post.client_id,
            account_id=created_post.account_id,
            content_lab_id=created_post.content_lab_id,
            content_type=created_post.content_type,
            text_content=created_post.text_content,
            image_url=created_post.image_url,
            hashtags=created_post.hashtags,
            scheduled_date=created_post.scheduled_date,
            scheduled_time=created_post.scheduled_time,
            timezone=created_post.timezone,
            status=created_post.status,
            agent_assigned=created_post.agent_assigned,
            is_active=created_post.is_active,
            created_at=created_post.created_at.isoformat() if created_post.created_at else "",
            updated_at=created_post.updated_at.isoformat() if created_post.updated_at else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(500, f"Failed to schedule post: {str(e)}")
