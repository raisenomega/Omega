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

        # 2. Verify client exists
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        # 3. Propiedad por DATOS server-side. NO se usa el claim `role` (sale de
        #    user_metadata, editable por el user → escalada de privilegios · guardian).
        #    Permite: dueño de la fila (user_id) O reseller que la gestiona O superadmin real.
        rid = client.get("reseller_id")
        owned_resellers = await client_repository.get_owned_reseller_ids(user_id)
        is_row_owner = str(client.get("user_id")) == str(user_id)
        is_managing_reseller = bool(rid) and str(rid) in owned_resellers
        is_superadmin = await client_repository.is_platform_superadmin(user_id)
        if not (is_row_owner or is_managing_reseller or is_superadmin):
            raise HTTPException(
                status_code=403,
                detail="No autorizado para eliminar este cliente"
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
