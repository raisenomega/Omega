"""
Context Update Endpoint
Handles client context profile updates
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from datetime import datetime, timezone

from app.api.routes.context.models import (
    ClientContextUpdate,
    ClientContextResponse,
    ClientContextData
)
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.repositories.context_repository import context_repository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.patch("/{client_id}", response_model=ClientContextResponse)
async def update_client_context(
    client_id: str,
    request: ClientContextUpdate,
    authorization: Optional[str] = Header(None)
) -> ClientContextResponse:
    """
    Update client context profile (partial update).

    Args:
        client_id: Client UUID
        request: Context update payload (only provided fields will be updated)
        authorization: JWT bearer token

    Returns:
        ClientContextResponse with updated context data

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to update another client's context
        HTTPException 404: Context not found for this client
        HTTPException 500: Database or unexpected error

    Security:
        Verifies authenticated client_id matches requested client_id

    Notes:
        - Only provided fields in request will be updated (exclude_unset=True)
        - Version is automatically incremented on each update
        - updated_at timestamp is automatically set
    """
    try:
        # Verify client is updating their own context
        authenticated_client_id = await get_current_user_id(authorization)
        if authenticated_client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot update another client's context"
            )

        # Check if context exists
        existing_context = await context_repository.get_client_context(client_id)
        if not existing_context:
            raise HTTPException(
                status_code=404,
                detail="Context not found for this client. Use POST to create."
            )

        # Update only provided fields (exclude_unset=True)
        update_data = request.model_dump(exclude_unset=True)

        # Increment version and update timestamp
        update_data["version"] = existing_context.get("version", 1) + 1
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Update context in database
        updated_context = await context_repository.update_client_context(
            client_id,
            update_data
        )

        logger.info(f"Context updated for client {client_id}")
        return ClientContextResponse(
            success=True,
            data=ClientContextData(**updated_context),
            message="Context profile updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating context"
        )
