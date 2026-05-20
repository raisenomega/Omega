"""Pydantic models · GET + PATCH /clients/profile."""
from typing import Optional
from pydantic import BaseModel, Field


class ClientProfileResponse(BaseModel):
    id: str
    name: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    aria_level: Optional[int] = None


class UpdateClientProfileRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    industry: Optional[str] = Field(default=None, max_length=64)
    region: Optional[str] = Field(default=None, max_length=64)
