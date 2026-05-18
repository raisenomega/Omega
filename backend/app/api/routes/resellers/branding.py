"""
Reseller Branding Routes
Endpoints for managing white-label branding and media uploads
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import BrandingRequest
from ._branding_get_handler import handle_get_branding
from ._branding_upload_handler import handle_upload_hero_media
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{reseller_id}/branding", response_model=APIResponse)
async def update_branding(reseller_id: str, request: BrandingRequest) -> APIResponse:
    """Create or update reseller branding (colors, copy, sections, contact, pricing)."""
    try:
        service = get_supabase_service()
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        branding_data = request.model_dump(exclude_none=True)
        branding = await service.update_branding(reseller_id, branding_data)

        return APIResponse(success=True, data=branding, message="Branding updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reseller_id}/branding", response_model=APIResponse)
async def get_branding(reseller_id: str) -> APIResponse:
    """Get reseller branding config with defaults if not yet configured."""
    try:
        service = get_supabase_service()
        branding = await handle_get_branding(service, reseller_id)
        return APIResponse(success=True, data=branding, message="Branding retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting branding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/upload-hero-media", response_model=APIResponse)
async def upload_hero_media(reseller_id: str, file: UploadFile = File(...)) -> APIResponse:
    """Upload hero media (video/image, max 15MB) to Supabase Storage."""
    try:
        service = get_supabase_service()
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        result = await handle_upload_hero_media(service, reseller, reseller_id, file)
        return APIResponse(success=True, data=result, message="Hero media uploaded successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading hero media: {e}")
        raise HTTPException(status_code=500, detail=str(e))
