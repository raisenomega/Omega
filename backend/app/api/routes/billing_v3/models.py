"""Pydantic request/response models para billing_v3 routes."""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreateCheckoutRequest(BaseModel):
    """Payload del POST /create-checkout-session.

    target_plan: 'basic' o 'pro' · 'adopcion' rechazado (trial gratis ·
    trigger auto-provision lo cubre · ver migración 00006).
    """
    client_id: str = Field(..., description="UUID del cliente que hace upgrade")
    target_plan: Literal["basic", "pro"] = Field(
        ..., description="Plan al que se quiere migrar"
    )


class CreateCheckoutResponse(BaseModel):
    """Respuesta del POST /create-checkout-session."""
    success: bool
    checkout_url: Optional[str] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
