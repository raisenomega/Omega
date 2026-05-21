"""Pydantic models · GET /content/ y PATCH /content/{id}/save."""
from typing import Optional
from pydantic import BaseModel


class ContentItem(BaseModel):
    id: str
    client_id: str
    platform: Optional[str] = None
    content_type: str
    content: str
    model: Optional[str] = None
    is_saved: bool
    created_at: str


class ContentListResponse(BaseModel):
    items: list[ContentItem]
    total: int


class SaveContentRequest(BaseModel):
    is_saved: bool
