"""
Reseller Admin Routes
OMEGA owner-only endpoints for reseller management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.infrastructure.supabase_service import get_supabase_service
from app.config import settings
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    CreateResellerRequest,
    UpdateResellerStatusRequest,
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create", response_model=APIResponse)
async def create_reseller(request: CreateResellerRequest) -> APIResponse:
    """
    Create new reseller account (OMEGA owner only)

    Args:
        request: Reseller creation data (slug, agency_name, owner_email, owner_name)

    Returns:
        APIResponse with created reseller data and temporary password

    Raises:
        HTTPException 400: Slug already exists
        HTTPException 500: Server error

    Creates:
        - Reseller in resellers table
        - Default branding configuration
        - Client account with role='reseller' for authentication
    """
    # SIGNUP GATE: crea un clients role='reseller' vía service-role SIN auth (2da puerta
    # pública de creación de cuentas). Misma barrera que /register · default cerrado en prod.
    # (Endurecer con auth superadmin = follow-up · ver CHECKLIST PRE-ONBOARDING-EXTERNO.)
    if not settings.signup_enabled:
        raise HTTPException(status_code=403, detail="signups_closed")
    try:
        service = get_supabase_service()

        # Check if slug already exists
        existing = await service.get_reseller_by_slug(request.slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Slug '{request.slug}' already exists"
            )

        # Provisioning completo de reseller (fila en resellers + branding + cuenta de
        # login) exige owner_user_id (NOT NULL → auth.users) y el schema reseller
        # definitivo del Modelo C. Hoy ese schema está en drift: las columnas que el
        # modelo Pydantic asume (agency_name, owner_email, owner_name, etc.) NO existen
        # en la tabla real → DEBT-SCHEMA-DRIFT-RESELLER, diferido a Sprint 8.
        # Hasta entonces degradamos honesto con 501 en vez de intentar un INSERT roto
        # (que daría 500 por columnas fantasma / owner_user_id faltante).
        raise HTTPException(
            status_code=501,
            detail="reseller_provisioning_pending_sprint8",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reseller: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=APIResponse)
async def get_all_resellers() -> APIResponse:
    """
    Get all resellers (OMEGA owner only)

    Returns:
        APIResponse with list of all resellers and status counters

    Counters include:
        - total: Total number of resellers
        - active: Resellers with status='active'
        - suspended: Resellers with status='suspended'
        - with_mora: Resellers with days_overdue > 0
    """
    try:
        service = get_supabase_service()

        resellers = await service.get_all_resellers()

        # Calculate status counters
        total = len(resellers)
        active = len([r for r in resellers if r.get("status") == "active"])
        suspended = len([r for r in resellers if r.get("status") == "suspended"])
        with_mora = len([r for r in resellers if r.get("days_overdue", 0) > 0])

        return APIResponse(
            success=True,
            data={
                "resellers": resellers,
                "total": total,
                "active": active,
                "suspended": suspended,
                "with_mora": with_mora
            },
            message=f"Found {total} resellers"
        )
    except Exception as e:
        logger.error(f"Error getting all resellers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{reseller_id}/status", response_model=APIResponse)
async def update_reseller_status(
    reseller_id: str,
    request: UpdateResellerStatusRequest
) -> APIResponse:
    """
    Update reseller status (OMEGA owner only)

    Args:
        reseller_id: Reseller UUID
        request: Status update data (status, suspend_switch)

    Returns:
        APIResponse with updated reseller data

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Server error

    Status options:
        - active: Normal operation
        - warning: Payment warning
        - suspended: Temporarily disabled
        - terminated: Permanently closed
    """
    try:
        service = get_supabase_service()

        # Get current reseller
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Prepare update data. 'status' es columna real. 'suspend_switch' es columna
        # fantasma (schema drift · DEBT-SCHEMA-DRIFT-RESELLER · Sprint 8) → se ignora
        # para no romper el UPDATE; se reactiva con el schema real del Modelo C.
        update_data: Dict[str, Any] = {}
        if request.status is not None:
            update_data["status"] = request.status

        if not update_data:
            return APIResponse(
                success=True,
                data=reseller,
                message="No changes applied",
            )

        # Update reseller
        updated_reseller = await service.update_reseller(reseller_id, update_data)

        return APIResponse(
            success=True,
            data=updated_reseller,
            message="Reseller status updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reseller status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
