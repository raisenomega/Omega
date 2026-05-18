"""
Reseller Admin Routes
OMEGA owner-only endpoints for reseller management
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import (
    CreateResellerRequest,
    UpdateResellerStatusRequest,
)
import logging
import bcrypt

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
    try:
        service = get_supabase_service()

        # Check if slug already exists
        existing = await service.get_reseller_by_slug(request.slug)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Slug '{request.slug}' already exists"
            )

        # Create reseller
        reseller_data = request.model_dump()
        reseller = await service.create_reseller(reseller_data)

        # Create default branding
        branding_data: Dict[str, Any] = {
            "reseller_id": reseller["id"],
            "primary_color": "38 85% 55%",
            "secondary_color": "225 12% 14%",
            "badge_text": "Boutique Creative Agency",
            "hero_cta_text": "Comenzar"
        }
        await service.create_branding(branding_data)

        # Generate temporary password and hash
        temp_password = "TempAccess2026!"
        password_hash = bcrypt.hashpw(
            temp_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create client account for reseller authentication
        try:
            # Check if client account already exists
            existing_client = service.client.table("clients")\
                .select("id, email")\
                .eq("email", request.owner_email)\
                .execute()

            if not existing_client.data or len(existing_client.data) == 0:
                # Create new client account
                client_data: Dict[str, Any] = {
                    "name": request.owner_name,
                    "email": request.owner_email,
                    "password_hash": password_hash,
                    "role": "reseller",
                    "reseller_id": reseller["id"],
                    "status": "active",
                    "plan": "enterprise",
                    "subscription_status": "active",
                    "trial_active": False
                }

                service.client.table("clients").insert(client_data).execute()

                logger.info(
                    f"Client account created for reseller: {request.owner_email}"
                )
            else:
                # Update existing client with reseller role and ID
                service.client.table("clients")\
                    .update({
                        "role": "reseller",
                        "reseller_id": reseller["id"],
                        "password_hash": password_hash
                    })\
                    .eq("email", request.owner_email)\
                    .execute()

                logger.info(
                    f"Client account updated for reseller: {request.owner_email}"
                )
        except Exception as client_error:
            logger.warning(
                f"Could not create/update client account: {client_error}"
            )

        return APIResponse(
            success=True,
            data={
                **reseller,
                "temp_password": temp_password,
                "note": "Temporary password created. User should change it after first login."
            },
            message=f"Reseller '{request.agency_name}' created successfully"
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

        # Prepare update data
        update_data: Dict[str, Any] = {}
        if request.status is not None:
            update_data["status"] = request.status
        if request.suspend_switch is not None:
            update_data["suspend_switch"] = request.suspend_switch

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
