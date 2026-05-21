"""Pydantic models · GET /calendar/ + PATCH /calendar/{id}/status."""
from typing import Optional
from pydantic import BaseModel


class CalendarPost(BaseModel):
    id: str
    client_id: str
    platform: Optional[str] = None
    content_preview: str = ""
    scheduled_for: str
    status: str
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None


class CalendarListResponse(BaseModel):
    items: list[CalendarPost]
    total: int


class UpdateStatusRequest(BaseModel):
    status: str
