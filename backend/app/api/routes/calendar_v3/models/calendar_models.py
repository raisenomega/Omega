"""Pydantic models · GET /calendar/ + PATCH /calendar/{id}/status +
POST /calendar-v3/schedule/ (DEBT-CL-017 + path X)."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


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
    (MIN_HORAS_ENTRE_POSTS=2 · reparto bulk 3/día propio · desacoplado del límite de REX por red).
    Atomic insert · todos o ninguno.
    """
    client_id: str = Field(..., description="Client UUID")
    platform: str = Field(..., max_length=32, description="instagram/facebook/... (seed FormBar · legacy single-red)")
    platforms: Optional[list[str]] = Field(default=None, description="E · redes marcadas (fan-out). Si presente y no vacia -> 1 row por red active resuelta. None/vacio -> usa 'platform' (flujo legacy single-red · honra social_account_id)")
    content_ids: list[str] = Field(..., min_length=1, description="content_lab_generated.id de cada anchor del bloque · 1+")
    scheduled_for: datetime = Field(..., description="Timestamp UTC del PRIMER post · backend espacia los siguientes")
    media_url: Optional[str] = Field(default=None, description="URL Storage compartida entre todos los N posts del bloque")
    placement: Literal["feed", "story", "both"] = Field(default="feed", description="AMBAS · feed=post normal · story=historia (IG/FB) · both=feed+historia (2 filas/red que soporte story). Default feed = retrocompat")
    is_story: bool = Field(default=False, description="DEPRECADO (Pieza 3) · alias de placement='story' · solo para deploy-skew (front viejo). Usar 'placement'. Se quita el próximo cleanup")
    social_account_id: Optional[str] = Field(default=None, description="DEBT-CL-015 · si user eligió cuenta específica (N>1 cuentas por platform) · sino backend resuelve primera activa")
    force_brand_voice: bool = Field(default=False, description="X5 · override humano del gate de voz de marca · agenda bajo responsabilidad (queda auditado en agent_memory)")

    @field_validator("scheduled_for")
    @classmethod
    def _scheduled_for_tz_aware(cls, v: datetime) -> datetime:
        """Bug tz (11 jun): NUNCA asumir UTC para un naive · el front manda la hora
        del usuario como UTC explícito (Z u offset). Naive → 422 (fail-honest)."""
        if v.tzinfo is None:
            raise ValueError("scheduled_for_must_be_tz_aware · enviá la hora con offset o Z (no se asume UTC)")
        return v

    @model_validator(mode="after")
    def _derive_placement_from_alias(self) -> "ScheduledPostV3Create":
        """Deploy-skew: front viejo manda is_story=True sin placement → placement='story'.
        El placement explícito SIEMPRE gana (el alias solo actúa si placement quedó en el default)."""
        if self.is_story and self.placement == "feed":
            self.placement = "story"
        return self


class ScheduledPostV3Response(BaseModel):
    id: str
    client_id: str
    social_account_id: Optional[str] = None
    content_id: Optional[str] = None
    scheduled_for: str
    status: str
    media_url: Optional[str] = None
    brand_voice_skipped: bool = False    # X5 · cliente sin voz de marca definida (agendó sin filtro · 11 jun)
    below_brand_bar: bool = False        # X5 · algún post 0.5–0.7: pasó pero genérico/no-es-la-voz (damage gate)
