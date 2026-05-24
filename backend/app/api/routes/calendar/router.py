"""Calendar Router · 4 endpoints · auth + RBAC obligatorios (DEBT-CL-013 + C)."""
from typing import Optional
from fastapi import APIRouter, Header, Query

from .models import (
    ScheduledPostCreate, ScheduledPostUpdate, ScheduledPostResponse,
    ScheduledPostListResponse, DeleteResponse,
)
from .handlers import (
    handle_schedule_post, handle_list_posts, handle_update_post, handle_delete_post,
)

router = APIRouter(prefix="/calendar", tags=["Calendar 📅"])


@router.post("/schedule/", response_model=ScheduledPostResponse, status_code=201)
async def schedule_post(
    request: ScheduledPostCreate,
    authorization: Optional[str] = Header(None),
) -> ScheduledPostResponse:
    return await handle_schedule_post(request, authorization)


@router.get("/", response_model=ScheduledPostListResponse)
async def list_posts(
    authorization: Optional[str] = Header(None),
    account_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
) -> ScheduledPostListResponse:
    return await handle_list_posts(authorization, account_id, client_id, user_id, limit, offset, status)


@router.patch("/{post_id}/", response_model=ScheduledPostResponse)
async def update_post(
    post_id: str,
    request: ScheduledPostUpdate,
    authorization: Optional[str] = Header(None),
) -> ScheduledPostResponse:
    return await handle_update_post(post_id, request, authorization)


@router.delete("/{post_id}/", response_model=DeleteResponse)
async def delete_post(
    post_id: str,
    authorization: Optional[str] = Header(None),
) -> DeleteResponse:
    return await handle_delete_post(post_id, authorization)
