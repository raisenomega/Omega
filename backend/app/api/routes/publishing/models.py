"""Pydantic models · POST /api/v1/publish/auto."""
from typing import Optional

from pydantic import BaseModel, Field


class AutoPublishRequest(BaseModel):
    scheduled_post_id: str = Field(..., description="scheduled_posts.id YA aprobado/programado (status='pending')")
    client_id: str = Field(..., description="negocio ACTIVO del switcher (Switcher V1) · se valida ownership (DEBT-LIMIT1)")


class AutoPublishResponse(BaseModel):
    published: bool
    platform_post_id: Optional[str] = None
    error: Optional[str] = None
