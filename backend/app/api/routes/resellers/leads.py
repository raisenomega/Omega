"""
Reseller Lead Management Routes
Endpoints for managing leads generated from landing pages
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    CreateLeadRequest,
    UpdateLeadStatusRequest,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{reseller_id}/leads", response_model=APIResponse)
async def create_lead(
    reseller_id: str,
    request: CreateLeadRequest
) -> APIResponse:
    """
    Create lead from landing page contact form

    Args:
        reseller_id: Reseller UUID
        request: Lead data (name, email, phone, message)

    Returns:
        APIResponse with success status

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Server error

    Used by authenticated dashboard to manually create leads
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Create lead
        lead_data: Dict[str, Any] = {
            "reseller_id": reseller_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "message": request.message
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
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reseller_id}/leads", response_model=APIResponse)
async def get_reseller_leads(
    reseller_id: str,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> APIResponse:
    """
    Get all leads for a reseller with optional filters and pagination

    Args:
        reseller_id: Reseller UUID
        status: Optional filter (new|contacted|converted|lost)
        page: Page number (default: 1)
        limit: Results per page (default: 20, max: 100)

    Returns:
        APIResponse with paginated leads and counts by status

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Server error
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Validate limit
        if limit > 100:
            limit = 100

        # Get leads with pagination
        leads, total = await service.get_reseller_leads(
            reseller_id,
            status,
            page,
            limit
        )

        # Get counts by status
        counts = await service.get_lead_counts(reseller_id)

        return APIResponse(
            success=True,
            data={
                "leads": leads,
                "total": total,
                "page": page,
                "limit": limit,
                "counts": counts
            },
            message=f"Found {total} leads"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reseller leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads/{lead_id}", response_model=APIResponse)
async def get_lead(lead_id: str) -> APIResponse:
    """
    Get a specific lead by ID

    Args:
        lead_id: Lead UUID

    Returns:
        APIResponse with complete lead object

    Raises:
        HTTPException 404: Lead not found
        HTTPException 500: Server error
    """
    try:
        service = get_supabase_service()

        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return APIResponse(
            success=True,
            data=lead,
            message="Lead retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/leads/{lead_id}/status", response_model=APIResponse)
async def update_lead_status(
    lead_id: str,
    request: UpdateLeadStatusRequest
) -> APIResponse:
    """
    Update lead status and optional notes

    Args:
        lead_id: Lead UUID
        request: Status update data (status, notes)

    Returns:
        APIResponse with updated lead object

    Raises:
        HTTPException 404: Lead not found
        HTTPException 400: Invalid status
        HTTPException 500: Server error

    Logic:
        - If status = "contacted" → sets contacted_at = NOW()
        - If status = "converted" → sets contacted_at if null

    Valid statuses: new, contacted, converted, lost
    """
    try:
        service = get_supabase_service()

        # Verify lead exists
        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Validate status
        valid_statuses = ["new", "contacted", "converted", "lost"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )

        # Update lead status
        updated_lead = await service.update_lead_status(
            lead_id,
            request.status,
            request.notes
        )

        return APIResponse(
            success=True,
            data=updated_lead,
            message="Lead status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
