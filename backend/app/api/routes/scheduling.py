"""
Scheduling API Routes
Endpoints for content scheduling and queue management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.agents.scheduling_agent import scheduling_agent

router = APIRouter(prefix="/scheduling", tags=["scheduling"])


# Request Models
class SchedulePostRequest(BaseModel):
    """Request for scheduling a post"""
    post_data: dict[str, str | List] = Field(..., description="Post data")
    client_preferences: dict[str, str] = Field(..., description="Client preferences")


class GetQueueRequest(BaseModel):
    """Request for getting publication queue"""
    client_id: str = Field(..., description="Client ID")
    status_filter: str | None = Field(None, description="Filter by status")
    platform_filter: str | None = Field(None, description="Filter by platform")


class ApprovePostRequest(BaseModel):
    """Request for approving a post"""
    post_id: str = Field(..., description="Post ID to approve")
    reviewer_id: str = Field(..., description="Reviewer ID")
    approval_notes: str = Field("", description="Approval notes")


class OptimalTimesRequest(BaseModel):
    """Request for optimal posting times"""
    platform: str = Field(..., description="Target platform")
    audience_timezone: str = Field(..., description="Audience timezone")
    content_type: str = Field(..., description="Content type")


class BulkScheduleRequest(BaseModel):
    """Request for bulk scheduling"""
    posts: List[dict[str, str | List]] = Field(..., description="List of posts")
    client_id: str = Field(..., description="Client ID")
    spread_days: int = Field(7, description="Days to spread posts over")


# Response Model
class SchedulingAPIResponse(BaseModel):
    """Generic scheduling response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/schedule-post", response_model=SchedulingAPIResponse)
async def schedule_post(
    request: SchedulePostRequest
) -> SchedulingAPIResponse:
    """
    Create and schedule a post with optimal timing

    - **post_data**: Post data (caption, hashtags, media, etc.)
    - **client_preferences**: Client preferences (timezone, approval required)

    Returns scheduled post with optimal timing
    """
    try:
        result = await scheduling_agent.execute({
            "type": "schedule_post",
            "post_data": request.post_data,
            "client_preferences": request.client_preferences
        })

        return SchedulingAPIResponse(
            success=True,
            data=result,
            message="Post scheduled successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/{client_id}", response_model=SchedulingAPIResponse)
async def get_queue(
    client_id: str,
    status_filter: str | None = None,
    platform_filter: str | None = None
) -> SchedulingAPIResponse:
    """
    Get publication queue with filters

    - **client_id**: Client identifier
    - **status_filter**: Optional status filter
    - **platform_filter**: Optional platform filter

    Returns publication queue with stats and posts
    """
    try:
        result = await scheduling_agent.execute({
            "type": "get_queue",
            "client_id": client_id,
            "status_filter": status_filter,
            "platform_filter": platform_filter
        })

        return SchedulingAPIResponse(
            success=True,
            data=result,
            message="Queue retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-post", response_model=SchedulingAPIResponse)
async def approve_post(
    request: ApprovePostRequest
) -> SchedulingAPIResponse:
    """
    Approve post for publication - human in the loop

    - **post_id**: Post ID to approve
    - **reviewer_id**: Reviewer identifier
    - **approval_notes**: Optional approval notes

    Returns approved post
    """
    try:
        result = await scheduling_agent.execute({
            "type": "approve_post",
            "post_id": request.post_id,
            "reviewer_id": request.reviewer_id,
            "approval_notes": request.approval_notes
        })

        return SchedulingAPIResponse(
            success=True,
            data=result,
            message="Post approved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimal-times", response_model=SchedulingAPIResponse)
async def calculate_optimal_times(
    request: OptimalTimesRequest
) -> SchedulingAPIResponse:
    """
    Calculate best posting times based on platform and audience

    - **platform**: Target platform
    - **audience_timezone**: Audience timezone
    - **content_type**: Content type

    Returns optimal time slots with expected engagement boost
    """
    try:
        result = await scheduling_agent.execute({
            "type": "calculate_optimal_times",
            "platform": request.platform,
            "audience_timezone": request.audience_timezone,
            "content_type": request.content_type
        })

        return SchedulingAPIResponse(
            success=True,
            data=result,
            message="Optimal times calculated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-schedule", response_model=SchedulingAPIResponse)
async def bulk_schedule(
    request: BulkScheduleRequest
) -> SchedulingAPIResponse:
    """
    Schedule multiple posts distributed over time

    - **posts**: List of posts to schedule
    - **client_id**: Client identifier
    - **spread_days**: Days to spread posts over (default: 7)

    Returns list of scheduled posts
    """
    try:
        result = await scheduling_agent.execute({
            "type": "bulk_schedule",
            "posts": request.posts,
            "client_id": request.client_id,
            "spread_days": request.spread_days
        })

        return SchedulingAPIResponse(
            success=True,
            data={"scheduled_posts": result, "count": len(result)},
            message=f"Bulk scheduled {len(result)} posts over {request.spread_days} days"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Scheduling Agent status"""
    return scheduling_agent.get_status()
