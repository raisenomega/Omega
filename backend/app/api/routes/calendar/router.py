"""
Calendar Router
FastAPI REST endpoints for scheduled posts
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query

from .models import (
    ScheduledPostCreate,
    ScheduledPostUpdate,
    ScheduledPostResponse,
    ScheduledPostListResponse,
    DeleteResponse
)
from .handlers import (
    handle_schedule_post,
    handle_list_posts,
    handle_update_post,
    handle_delete_post
)

router = APIRouter(prefix="/calendar", tags=["Calendar 📅"])


@router.post("/schedule/", response_model=ScheduledPostResponse, status_code=201)
async def schedule_post(request: ScheduledPostCreate) -> ScheduledPostResponse:
    """
    Schedule a new social media post

    Validates plan limits before scheduling:
    - **basico_97**: 2 posts per day
    - **pro_197**: 5 posts per day
    - **enterprise_497**: unlimited

    Returns:
        Scheduled post details with ID and status
    """
    return await handle_schedule_post(request)


@router.get("/", response_model=ScheduledPostListResponse)
async def list_posts(
    account_id: str = Query(None, description="Social account UUID"),
    client_id: str = Query(None, description="Client UUID"),
    user_id: str = Query(None, description="User UUID - returns posts from all user's clients"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: str = Query(None, description="Filter by status: draft, scheduled, published, failed")
) -> ScheduledPostListResponse:
    """
    List scheduled posts - provide ONE of: account_id, client_id, or user_id

    **account_id**: Posts for specific social account
    **client_id**: Posts from all accounts of this client
    **user_id**: Posts from all clients owned by this user (auto-discovers clients)

    Returns paginated list ordered by scheduled date/time.
    Optional status filter to show only posts in a specific state.
    """
    return await handle_list_posts(account_id, client_id, user_id, limit, offset, status)


@router.patch("/{post_id}/", response_model=ScheduledPostResponse)
async def update_post(
    post_id: str,
    request: ScheduledPostUpdate
) -> ScheduledPostResponse:
    """
    Update scheduled post

    Only draft, scheduled, or failed posts can be edited.
    Posts being published cannot be modified.
    """
    return await handle_update_post(post_id, request)


@router.delete("/{post_id}/", response_model=DeleteResponse)
async def delete_post(post_id: str) -> DeleteResponse:
    """
    Cancel scheduled post (soft delete)

    Sets is_active=False. Cannot delete posts while publishing.
    """
    return await handle_delete_post(post_id)
