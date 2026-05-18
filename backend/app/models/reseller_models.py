"""
Reseller Domain Models
Pydantic models for multi-tenant reseller management
"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, date


def sanitize_json_field(val: Any) -> Dict[str, Any]:
    """
    Sanitize JSONB fields to ensure they're always dicts, never lists.
    Prevents frontend errors when Supabase returns [] instead of {}.
    """
    if isinstance(val, list):
        return {}
    if val is None:
        return {}
    if isinstance(val, dict):
        return val
    return {}


# RESELLER MODELS

class CreateResellerRequest(BaseModel):
    """Request to create new reseller account"""
    slug: str = Field(..., description="URL slug (e.g., 'agenciajuan')", min_length=3, max_length=50)
    agency_name: str = Field(..., description="Agency name", min_length=2, max_length=255)
    owner_email: EmailStr = Field(..., description="Owner email address")
    owner_name: str = Field(..., description="Owner full name", min_length=2, max_length=255)


class ResellerResponse(BaseModel):
    """Complete reseller object"""
    id: str
    slug: str
    agency_name: str
    owner_email: str
    owner_name: str
    stripe_account_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    white_label_active: bool
    status: str
    omega_commission_rate: float
    monthly_revenue_reported: float
    payment_due_date: Optional[date] = None
    days_overdue: int
    suspend_switch: bool
    clients_migrated: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UpdateResellerStatusRequest(BaseModel):
    """Request to update reseller status (OMEGA admin only)"""
    status: Optional[str] = Field(None, description="Status: active/warning/suspended/terminated")
    suspend_switch: Optional[bool] = Field(None, description="Manual suspension switch")


# BRANDING MODELS

class BrandingRequest(BaseModel):
    """Request to create/update reseller branding"""
    agency_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = Field(default="38 85% 55%", description="HSL or hex color")
    secondary_color: str = Field(default="225 12% 14%", description="HSL or hex color")
    hero_type: Optional[str] = Field(None, description="'image' or 'video'")
    hero_media_type: Optional[str] = Field(None, description="'image' or 'video' (alias for hero_type)")
    hero_media_url: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    hero_cta_text: str = Field(default="Comenzar")
    hero_cta_url: Optional[str] = None
    pain_section: Optional[Dict[str, Any]] = None
    solutions_section: Optional[Dict[str, Any]] = None
    services_section: Optional[Dict[str, Any]] = None
    metrics_section: Optional[Dict[str, Any]] = None
    process_section: Optional[Dict[str, Any]] = None
    testimonials_section: Optional[Dict[str, Any]] = None
    client_logos_section: Optional[Dict[str, Any]] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    footer_text: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None
    pricing_plans: Optional[List[Dict[str, Any]]] = None
    # Legacy fields (backward compatibility)
    agency_tagline: Optional[str] = None
    badge_text: Optional[str] = None
    pain_items: Optional[List[str]] = None
    solution_items: Optional[List[str]] = None
    services: Optional[List[Dict[str, str]]] = None
    metrics: Optional[List[Dict[str, Any]]] = None
    process_steps: Optional[List[Dict[str, str]]] = None
    testimonials: Optional[List[Dict[str, str]]] = None
    footer_email: Optional[str] = None
    footer_phone: Optional[str] = None
    legal_pages: Optional[List[Dict[str, str]]] = None


class BrandingResponse(BaseModel):
    """Complete branding object"""
    id: str
    reseller_id: str
    logo_url: Optional[str]
    hero_media_url: Optional[str]
    hero_media_type: Optional[str]
    primary_color: str
    secondary_color: str
    agency_tagline: Optional[str]
    badge_text: str
    hero_cta_text: str
    pain_items: List[str]
    solution_items: List[str]
    services: List[Dict[str, str]]
    metrics: List[Dict[str, Any]]
    process_steps: List[Dict[str, str]]
    testimonials: List[Dict[str, str]]
    footer_email: Optional[str]
    footer_phone: Optional[str]
    social_links: List[Dict[str, str]]
    legal_pages: List[Dict[str, str]]
    created_at: datetime
    updated_at: Optional[datetime]


class MediaUploadResponse(BaseModel):
    """Media upload response"""
    url: str
    media_type: str


# CLIENT MODELS

class AddClientRequest(BaseModel):
    """Request to assign client to reseller"""
    client_id: str = Field(..., description="Client UUID to assign")


class ClientSummary(BaseModel):
    """Client summary for dashboard"""
    id: str
    name: str
    status: str
    created_at: datetime


# LEAD MODELS

class CreateLeadRequest(BaseModel):
    """Request to create lead from landing page contact form"""
    name: str = Field(..., description="Contact name", min_length=2, max_length=255)
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    message: Optional[str] = Field(None, description="Contact message", max_length=2000)
    reseller_id: str = Field(..., description="Reseller UUID")


class CreateLeadBySlugRequest(BaseModel):
    """Request to create lead from public landing page (by slug)"""
    name: str = Field(..., description="Contact name", min_length=2, max_length=255)
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    message: Optional[str] = Field(None, description="Contact message", max_length=2000)
    source: str = Field(default="landing_page", description="Lead source")


class UpdateLeadStatusRequest(BaseModel):
    """Request to update lead status"""
    status: str = Field(..., description="new|contacted|converted|lost")
    notes: Optional[str] = Field(None, description="Optional notes")


# DASHBOARD MODELS

class ResellerDashboardResponse(BaseModel):
    """Complete reseller dashboard data"""
    reseller: ResellerResponse
    clients: List[Dict[str, Any]]
    agents: List[Dict[str, Any]]
    total_revenue: float
    omega_commission: float
    active_clients_count: int
    suspended_clients_count: int
