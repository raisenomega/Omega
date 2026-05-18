"""
OMEGA · Upsell Solicitudes Models
R-LINES-001: < 200L · R-DDD-001: Router → Service → Repository
"""
from typing import Optional
from pydantic import BaseModel, Field


class SolicitudCreate(BaseModel):
    client_id: str
    current_plan: str
    request_type: str = Field(..., pattern="^(individual_agent|full_department)$")
    item_name: str
    item_code: str
    monthly_price: float
    new_monthly_total: float
    client_message: Optional[str] = None


class SolicitudResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    client_email: str
    current_plan: str
    request_type: str
    item_name: str
    item_code: str
    monthly_price: float
    new_monthly_total: float
    client_message: Optional[str]
    status: str
    stripe_charge_id: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]


class SolicitudCreateResponse(BaseModel):
    success: bool
    data: Optional[SolicitudResponse] = None
    error: Optional[str] = None
    message: Optional[str] = None


class AdminSolicitudesResponse(BaseModel):
    success: bool
    data: Optional[list[SolicitudResponse]] = None
    total: Optional[int] = None
    pending_count: Optional[int] = None
    monthly_revenue_upsell: Optional[float] = None
    error: Optional[str] = None


class AdminSolicitudDetailResponse(BaseModel):
    success: bool
    data: Optional[SolicitudResponse] = None
    error: Optional[str] = None


class SolicitudActionResponse(BaseModel):
    success: bool
    data: Optional[SolicitudResponse] = None
    stripe_charge_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
