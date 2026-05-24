"""Pydantic models · GET /calendar/ + PATCH /calendar/{id}/status +
POST /calendar-v3/schedule/ (DEBT-CL-017 + path X)."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CalendarPost(BaseModel):
    id: str
    client_id: str
    platform: Optional[str] = None
    content_preview: str = ""
    scheduled_for: str
    status: str
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    media_url: Optional[str] = None  # DEBT-CL-017 · null si post texto puro


class CalendarListResponse(BaseModel):
    items: list[CalendarPost]
    total: int


class UpdateStatusRequest(BaseModel):
    status: str


class ScheduledPostV3Create(BaseModel):
    """Schema correcto V3 · DEBT-CL-017 + DEBT-031 partial. Frontend apunta
    a /api/v1/calendar-v3/schedule/. Cero cols inexistentes (legacy issue)."""
    client_id: str = Field(..., description="Client UUID")
    platform: str = Field(..., max_length=32, description="instagram/facebook/...")
    content_id: str = Field(..., description="content_lab_generated.id del anchor del bloque")
    scheduled_for: datetime = Field(..., description="Timestamp UTC ISO combinado date+time")
    media_url: Optional[str] = Field(default=None, description="URL Storage si el bloque incluye image/video")


class ScheduledPostV3Response(BaseModel):
    id: str
    client_id: str
    social_account_id: Optional[str] = None
    content_id: Optional[str] = None
    scheduled_for: str
    status: str
    media_url: Optional[str] = None
