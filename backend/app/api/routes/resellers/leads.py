"""
Reseller Lead Management Routes
Endpoints for managing leads generated from landing pages
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Any, Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    CreateLeadRequest,
    UpdateLeadStatusRequest,
)
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.auth.super_owner import is_super_owner_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Fuente única · alineados con los CHECK de leads en DB.
VALID_LEAD_STATUSES = ["new", "contacted", "qualified", "converted", "lost"]  # incluye 'qualified' · DEBT-LEADS-QUALIFIED
VALID_TEMPERATURES = ["frio", "tibio", "caliente", "convertido"]  # CHECK leads.temperature · 00089


async def _authz_reseller(authorization: Optional[str], reseller_id: str) -> None:
    """IDOR guard (list/create por reseller): super_owner ve todo · si no, debe ser el owner de ESE
    reseller. Sin token → 401 (get_current_user) · autenticado ajeno → 403."""
    user = await get_current_user(authorization)
    if await is_super_owner_id(user["id"]):
        return
    if user.get("reseller_id") != reseller_id:
        raise HTTPException(status_code=403, detail="forbidden")


async def _authz_lead(user: Dict[str, Any], lead: Dict[str, Any]) -> None:
    """IDOR guard (un lead ya fetcheado): super_owner ve todo · lead de plataforma (reseller_id NULL)
    → SOLO super_owner · lead de reseller → su owner. No-autorizado → 404 (no confirma el UUID)."""
    if await is_super_owner_id(user["id"]):
        return
    rid = lead.get("reseller_id")
    if rid is None or user.get("reseller_id") != rid:
        raise HTTPException(status_code=404, detail="Lead not found")


@router.post("/{reseller_id}/leads", response_model=APIResponse)
async def create_lead(
    reseller_id: str,
    request: CreateLeadRequest,
    authorization: Optional[str] = Header(None),
) -> APIResponse:
    """
    Create lead from landing page contact form (dashboard manual · owner del reseller o super_owner).
    La captura pública white-label vive en public.py /slug/{slug}/lead (sin auth) · este NO es esa.

    Args:
        reseller_id: Reseller UUID
        request: Lead data (name, email, phone, message)

    Returns:
        APIResponse with success status

    Raises:
        HTTPException 401/403: sin token / ajeno · 404: Reseller not found · 500: Server error
    """
    try:
        await _authz_reseller(authorization, reseller_id)
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
    limit: int = 20,
    authorization: Optional[str] = Header(None),
) -> APIResponse:
    """
    Get all leads for a reseller with optional filters and pagination (owner del reseller o super_owner)

    Args:
        reseller_id: Reseller UUID
        status: Optional filter (new|contacted|qualified|converted|lost)
        page: Page number (default: 1)
        limit: Results per page (default: 20, max: 100)

    Returns:
        APIResponse with paginated leads and counts by status

    Raises:
        HTTPException 401/403: sin token / ajeno · 404: Reseller not found · 500: Server error
    """
    try:
        await _authz_reseller(authorization, reseller_id)
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
async def get_lead(lead_id: str, authorization: Optional[str] = Header(None)) -> APIResponse:
    """
    Get a specific lead by ID (owner del reseller del lead · plataforma → super_owner)

    Args:
        lead_id: Lead UUID

    Returns:
        APIResponse with complete lead object

    Raises:
        HTTPException 401: sin token · 404: Lead not found / no autorizado · 500: Server error
    """
    try:
        user = await get_current_user(authorization)  # 401 si sin token (antes de tocar DB)
        service = get_supabase_service()

        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        await _authz_lead(user, lead)  # no-autorizado → 404 (no confirma existencia)

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
    request: UpdateLeadStatusRequest,
    authorization: Optional[str] = Header(None),
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
        user = await get_current_user(authorization)  # 401 si sin token (antes de tocar DB)
        service = get_supabase_service()

        # Verify lead exists
        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        await _authz_lead(user, lead)  # no-autorizado → 404 (no confirma existencia)

        # Valida status/temperature SOLO si vienen (alineados con sus CHECK en DB)
        if request.status is not None and request.status not in VALID_LEAD_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. One of: {', '.join(VALID_LEAD_STATUSES)}")
        if request.temperature is not None and request.temperature not in VALID_TEMPERATURES:
            raise HTTPException(status_code=400, detail=f"Invalid temperature. One of: {', '.join(VALID_TEMPERATURES)}")

        # Solo los campos provistos (None se omiten · el mixin whitelistea columnas)
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        updated_lead = await service.update_lead(lead_id, updates)

        return APIResponse(
            success=True,
            data=updated_lead,
            message="Lead updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/leads/{lead_id}", response_model=APIResponse)
async def delete_lead(lead_id: str, authorization: Optional[str] = Header(None)) -> APIResponse:
    """Elimina un lead (owner del reseller del lead · plataforma → super_owner). No-autorizado → 404.
    401 sin token · 404 lead inexistente / no autorizado."""
    try:
        user = await get_current_user(authorization)  # 401 si sin token
        service = get_supabase_service()
        lead = await service.get_lead_by_id(lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        await _authz_lead(user, lead)  # no-autorizado → 404 (no confirma existencia)
        await service.delete_lead(lead_id)
        return APIResponse(success=True, data={}, message="Lead deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))
