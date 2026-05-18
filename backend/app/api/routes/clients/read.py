"""
Client Read Endpoint
GET /clients/{client_id} - Get client profile
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.clients.models import ClientResponse, ClientProfile
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client_profile(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> ClientResponse:
    """
    Get client profile by ID.
    owner: any client, reseller: their clients, client: own profile only.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        user_id = user["id"]
        role = user["role"]

        # 2. Get client from database
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        # 3. Access control based on role
        if role == "reseller" and client.get("reseller_id") != user_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access client from another reseller"
            )

        if role == "client" and client_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access another client's profile"
            )

        return ClientResponse(
            success=True,
            data=ClientProfile(**client),
            message="Client retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving client"
        )
