"""
Client Update Endpoint
PATCH /clients/{client_id} - Update client fields
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.clients.models import ClientUpdate, ClientResponse, ClientProfile
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client_profile(
    client_id: str,
    request: ClientUpdate,
    authorization: Optional[str] = Header(None)
) -> ClientResponse:
    """
    Update client profile fields.
    owner: any client, reseller: their clients, client: forbidden.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        user_id = user["id"]
        role = user["role"]

        # 2. Only owner and reseller can update
        if role == "client":
            raise HTTPException(
                status_code=403,
                detail="Clients cannot update profiles. Contact your reseller."
            )

        # 3. Get client to verify existence
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        # 4. Reseller can only update their clients
        if role == "reseller" and client.get("reseller_id") != user_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot update client from another reseller"
            )

        # 5. Extract only provided fields
        update_data = request.model_dump(exclude_unset=True)

        # 6. Update client
        updated_client = await client_repository.update_client(client_id, update_data)

        logger.info(f"Client {client_id} updated by {role} {user_id}")

        return ClientResponse(
            success=True,
            data=ClientProfile(**updated_client),
            message="Client updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating client"
        )
