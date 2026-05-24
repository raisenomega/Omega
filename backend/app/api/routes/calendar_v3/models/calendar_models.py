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
    """Schema correcto V3 · DEBT-CL-017 + DEBT-018 (bulk).

    content_ids: 1+ items de texto del bloque · cada uno se programa como
    1 row separada · backend spread automático según LIMITS_OMEGA
    (MIN_HORAS_ENTRE_POSTS=2 · MAX_POSTS_AUTO_PER_DIA_CLIENTE=3).
    Atomic insert · todos o ninguno.
    """
    client_id: str = Field(..., description="Client UUID")
    platform: str = Field(..., max_length=32, description="instagram/facebook/...")
    content_ids: list[str] = Field(..., min_length=1, description="content_lab_generated.id de cada anchor del bloque · 1+")
    scheduled_for: datetime = Field(..., description="Timestamp UTC del PRIMER post · backend espacia los siguientes")
    media_url: Optional[str] = Field(default=None, description="URL Storage compartida entre todos los N posts del bloque")
    social_account_id: Optional[str] = Field(default=None, description="DEBT-CL-015 · si user eligió cuenta específica (N>1 cuentas por platform) · sino backend resuelve primera activa")


class ScheduledPostV3Response(BaseModel):
    id: str
    client_id: str
    social_account_id: Optional[str] = None
    content_id: Optional[str] = None
    scheduled_for: str
    status: str
    media_url: Optional[str] = None
