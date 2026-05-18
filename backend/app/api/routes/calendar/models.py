"""
Calendar API Models
Pydantic DTOs for request/response validation
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional, List
from datetime import date, time
from pydantic import BaseModel, Field

from app.domain.calendar.types import Status


class ScheduledPostCreate(BaseModel):
    """DTO for creating scheduled post"""
    account_id: str = Field(..., description="Social account UUID")
    content_lab_id: Optional[str] = Field(None, description="Content Lab reference")
    content_type: str = Field(..., description="Type of content (post, story, email, bio, etc.)")
    text_content: str = Field(..., min_length=1, max_length=5000)
    image_url: Optional[str] = Field(None, description="Image URL if applicable")
    hashtags: List[str] = Field(default_factory=list)
    scheduled_date: date = Field(..., description="Date to publish")
    scheduled_time: time = Field(..., description="Time to publish")
    timezone: str = Field(default="America/Puerto_Rico")

    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "cb1dfe0a-43a2-4e9b-9099-df6035f76700",
                "content_type": "post",
                "text_content": "Check out our new product! 🚀",
                "hashtags": ["tech", "innovation"],
                "scheduled_date": "2026-02-20",
                "scheduled_time": "14:30:00"
            }
        }


class ScheduledPostUpdate(BaseModel):
    """DTO for updating scheduled post"""
    content_type: Optional[str] = None
    text_content: Optional[str] = Field(None, min_length=1, max_length=5000)
    image_url: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    timezone: Optional[str] = None
    agent_assigned: Optional[str] = Field(None, description="Agent that assigned this post")

    class Config:
        json_schema_extra = {
            "example": {
                "text_content": "Updated caption! ✨",
                "hashtags": ["updated", "new"],
                "scheduled_date": "2026-02-21"
            }
        }


class ScheduledPostResponse(BaseModel):
    """DTO for scheduled post response"""
    id: str
    client_id: str
    account_id: str
    content_lab_id: Optional[str] = None
    content_type: str
    text_content: str
    image_url: Optional[str] = None
    hashtags: List[str]
    scheduled_date: date
    scheduled_time: time
    timezone: str
    status: Status
    agent_assigned: str
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "client_id": "bd68ca50-b8ef-4240-a0ce-44df58f53171",
                "account_id": "cb1dfe0a-43a2-4e9b-9099-df6035f76700",
                "content_type": "post",
                "text_content": "Great product announcement! 🚀",
                "hashtags": ["tech", "innovation"],
                "scheduled_date": "2026-02-20",
                "scheduled_time": "14:30:00",
                "timezone": "America/Puerto_Rico",
                "status": "scheduled",
                "is_active": True,
                "created_at": "2026-02-17T20:00:00Z",
                "updated_at": "2026-02-17T20:00:00Z"
            }
        }


class ScheduledPostListResponse(BaseModel):
    """DTO for list of scheduled posts"""
    items: List[ScheduledPostResponse]
    total: int
    limit: int
    offset: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "limit": 20,
                "offset": 0
            }
        }


class DeleteResponse(BaseModel):
    """DTO for delete confirmation"""
    id: str
    deleted: bool
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "deleted": True,
                "message": "Scheduled post cancelled successfully"
            }
        }
