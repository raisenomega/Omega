"""
Reseller Public Routes
Public endpoints for white-label landing pages (no authentication required)
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    CreateLeadBySlugRequest,
    sanitize_json_field,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/slug/{slug}", response_model=APIResponse)
async def get_branding_by_slug(slug: str) -> APIResponse:
    """
    Get reseller + branding by slug (PUBLIC endpoint)

    Args:
        slug: Reseller URL slug

    Returns:
        APIResponse with reseller and branding data

    Raises:
        No HTTPException - returns error in response

    Used by white-label landing pages to load all branding data

    Response codes:
        - success=True: Reseller found and active
        - success=False, error="not_found": Agency not found
        - success=False, error="agency_suspended": Agency suspended
    """
    try:
        service = get_supabase_service()

        # Get reseller by slug
        reseller = await service.get_reseller_by_slug(slug)
        if not reseller:
            return APIResponse(
                success=False,
                data={"error": "not_found"},
                message="Agency not found"
            )

        # Check if suspended
        if reseller.get("status") == "suspended":
            return APIResponse(
                success=False,
                data={"error": "agency_suspended"},
                message="This agency is not available"
            )

        # Get branding (or return defaults)
        branding = await service.get_branding(reseller["id"])
        if not branding:
            # Return default branding
            branding = {
                "reseller_id": reseller["id"],
                "primary_color": "38 85% 55%",
                "secondary_color": "225 12% 14%",
                "hero_cta_text": "Comenzar",
                "logo_url": None,
                "hero_type": None,
                "hero_media_url": None,
                "hero_title": None,
                "hero_subtitle": None,
                "hero_cta_url": None,
                "pain_section": {},
                "solutions_section": {},
                "services_section": {},
                "metrics_section": {},
                "process_section": {},
                "testimonials_section": {},
                "client_logos_section": {},
                "contact_email": None,
                "contact_phone": None,
                "footer_text": None,
                "social_links": {},
                "pricing_plans": []
            }
        else:
            # Sanitize JSONB fields to ensure they're always dicts, never lists
            branding["pain_section"] = sanitize_json_field(
                branding.get("pain_section")
            )
            branding["solutions_section"] = sanitize_json_field(
                branding.get("solutions_section")
            )
            branding["services_section"] = sanitize_json_field(
                branding.get("services_section")
            )
            branding["metrics_section"] = sanitize_json_field(
                branding.get("metrics_section")
            )
            branding["process_section"] = sanitize_json_field(
                branding.get("process_section")
            )
            branding["testimonials_section"] = sanitize_json_field(
                branding.get("testimonials_section")
            )
            branding["client_logos_section"] = sanitize_json_field(
                branding.get("client_logos_section")
            )
            branding["social_links"] = sanitize_json_field(
                branding.get("social_links")
            )

            # Ensure pricing_plans is always an array
            branding["pricing_plans"] = branding.get("pricing_plans") or []

        # Combine reseller + branding
        public_data: Dict[str, Any] = {
            "reseller": {
                "id": reseller["id"],
                "slug": reseller["slug"],
                "agency_name": reseller["agency_name"],
                "status": reseller["status"]
            },
            "branding": branding
        }

        return APIResponse(
            success=True,
            data=public_data,
            message="Reseller found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branding by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/slug/{slug}/lead", response_model=APIResponse)
async def create_lead_by_slug(
    slug: str,
    request: CreateLeadBySlugRequest
) -> APIResponse:
    """
    Create lead from public landing page using slug (PUBLIC endpoint)

    Args:
        slug: Reseller URL slug
        request: Lead data (name, email, phone, message, source)

    Returns:
        APIResponse with success status

    Raises:
        No HTTPException for not found - returns error in response

    Used by white-label landing pages to submit contact forms
    The reseller_id is automatically inferred from the slug
    """
    try:
        service = get_supabase_service()

        # Get reseller by slug
        reseller = await service.get_reseller_by_slug(slug)
        if not reseller:
            return APIResponse(
                success=False,
                data={"error": "not_found"},
                message="Agency not found"
            )

        # Create lead
        lead_data: Dict[str, Any] = {
            "reseller_id": reseller["id"],
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "message": request.message,
            "source": request.source
        }

        await service.create_lead(lead_data)

        return APIResponse(
            success=True,
            data={},
            message="Lead received successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead by slug: {e}")
        raise HTTPException(status_code=500, detail=str(e))
