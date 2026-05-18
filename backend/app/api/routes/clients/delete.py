"""
Client Delete Endpoint
DELETE /clients/{client_id} - Soft delete client
"""
from fastapi import APIRouter, HTTPException, Header, Response
from typing import Optional
import logging

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> Response:
    """
    Soft delete client (status = 'deleted').
    Only owner can delete.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        user_id = user["id"]
        role = user["role"]

        # 2. Only owner, super_admin, or admin can delete clients
        if role not in ("owner", "super_admin", "admin"):
            raise HTTPException(
                status_code=403,
                detail="Only platform owners can delete clients"
            )

        # 3. Verify client exists
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        # 4. Soft delete
        success = await client_repository.soft_delete_client(client_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete client"
            )

        logger.info(f"Client {client_id} deleted by owner {user_id}")

        return Response(status_code=204)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting client"
        )
