"""Pydantic request/response models para billing_v3 routes."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreateCheckoutRequest(BaseModel):
    """Payload del POST /create-checkout-session.

    target_plan: 'basic' o 'pro' · 'adopcion' rechazado (trial gratis ·
    trigger auto-provision lo cubre · ver migración 00006).
    """
    client_id: str = Field(..., description="UUID del cliente que hace upgrade")
    target_plan: Literal["basic", "pro", "enterprise"] = Field(
        ..., description="Plan al que se quiere migrar (enterprise self-serve · DEBT-076)"
    )


class ScheduleDowngradeRequest(BaseModel):
    """DEBT-076 · payload POST /billing/schedule-downgrade.

    target_plan: 'basic' o 'pro' · el downgrade se PROGRAMA a fin de ciclo
    (Stripe SubscriptionSchedule) · no es inmediato.
    """
    client_id: str = Field(..., description="UUID del cliente que baja de plan")
    target_plan: Literal["basic", "pro"] = Field(..., description="Plan menor destino")


class ScheduleDowngradeResponse(BaseModel):
    """Respuesta POST /billing/schedule-downgrade."""
    success: bool
    scheduled: Optional[bool] = None
    target_plan: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


class CreateCheckoutResponse(BaseModel):
    """Respuesta del POST /create-checkout-session."""
    success: bool
    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None


# DEBT-VID-001 · 3 video packs spec §4.4
VideoPackCodeStr = Literal["starter", "creator", "cinematic_pro"]


class VideoPackCheckoutRequest(BaseModel):
    """DEBT-VID-001 · payload POST /billing/checkout-video-pack."""
    video_pack_code: VideoPackCodeStr = Field(..., description="starter | creator | cinematic_pro")


class VideoPackCheckoutResponse(BaseModel):
    """Respuesta POST /billing/checkout-video-pack."""
    checkout_url: str
    session_id: str


# DEBT-052 FASE 4 · 4 credit packs (budget API prepagado · texto/imagen)
CreditPackCodeStr = Literal["micro", "starter", "plus", "ultra"]


class CreditPackCheckoutRequest(BaseModel):
    """DEBT-052 FASE 4 · payload POST /billing/checkout-credit-pack."""
    credit_pack_code: CreditPackCodeStr = Field(..., description="micro | starter | plus | ultra")


class CreditPackCheckoutResponse(BaseModel):
    """Respuesta POST /billing/checkout-credit-pack."""
    checkout_url: str
    session_id: str
