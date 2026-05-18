"""
Reseller Client Management Routes
Endpoints for managing clients assigned to resellers
"""
from fastapi import APIRouter, HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.reseller_models import AddClientRequest
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{reseller_id}/clients", response_model=APIResponse)
async def get_reseller_clients(reseller_id: str) -> APIResponse:
    """
    Get all clients assigned to a reseller

    Args:
        reseller_id: Reseller UUID

    Returns:
        APIResponse with list of clients and count

    Raises:
        HTTPException 500: Server error

    Returns list of clients with full data including:
        - Client details (name, email, status)
        - Subscription information
        - Usage metrics
        - Created/updated timestamps
    """
    try:
        service = get_supabase_service()

        clients = await service.get_reseller_clients(reseller_id)

        return APIResponse(
            success=True,
            data={"clients": clients, "count": len(clients)},
            message=f"Found {len(clients)} clients"
        )
    except Exception as e:
        logger.error(f"Error getting clients: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{reseller_id}/clients/add", response_model=APIResponse)
async def add_client_to_reseller(
    reseller_id: str,
    request: AddClientRequest
) -> APIResponse:
    """
    Assign existing client to reseller

    Args:
        reseller_id: Reseller UUID
        request: Client assignment data (client_id)

    Returns:
        APIResponse with updated client data

    Raises:
        HTTPException 404: Reseller or client not found
        HTTPException 500: Server error

    Updates the client's reseller_id field to associate them
    with the specified reseller account
    """
    try:
        service = get_supabase_service()

        # Verify reseller exists
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Assign client
        client = await service.assign_client_to_reseller(
            request.client_id,
            reseller_id
        )

        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        return APIResponse(
            success=True,
            data=client,
            message="Client assigned to reseller successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning client: {e}")
        raise HTTPException(status_code=500, detail=str(e))
