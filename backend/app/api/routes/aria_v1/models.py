"""Pydantic models para aria_v1 routes."""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ARIAMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class ARIAMessageResponse(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str
    aria_level: int


class ARIAConversationItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    aria_level: Optional[int] = None
    created_at: str


class ARIAHistoryResponse(BaseModel):
    messages: list[ARIAConversationItem]


class ARIATrackRequest(BaseModel):
    event_type: str = Field(..., max_length=64)
    event_data: Optional[dict] = None
    session_id: Optional[str] = None
