"""
Domain Models Package
Pydantic models for API requests/responses
"""
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    # Helper
    sanitize_json_field,
    # Reseller
    CreateResellerRequest,
    ResellerResponse,
    UpdateResellerStatusRequest,
    # Branding
    BrandingRequest,
    BrandingResponse,
    MediaUploadResponse,
    # Clients
    AddClientRequest,
    ClientSummary,
    # Leads
    CreateLeadRequest,
    CreateLeadBySlugRequest,
    UpdateLeadStatusRequest,
    # Dashboard
    ResellerDashboardResponse,
)

__all__ = [
    # Shared
    "APIResponse",
    # Helper
    "sanitize_json_field",
    # Reseller
    "CreateResellerRequest",
    "ResellerResponse",
    "UpdateResellerStatusRequest",
    # Branding
    "BrandingRequest",
    "BrandingResponse",
    "MediaUploadResponse",
    # Clients
    "AddClientRequest",
    "ClientSummary",
    # Leads
    "CreateLeadRequest",
    "CreateLeadBySlugRequest",
    "UpdateLeadStatusRequest",
    # Dashboard
    "ResellerDashboardResponse",
]
