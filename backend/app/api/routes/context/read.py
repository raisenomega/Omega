"""
Context Read Endpoint
Handles client context profile retrieval
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.context.models import (
    ClientContextResponse,
    ClientContextData
)
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.repositories.context_repository import context_repository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{client_id}", response_model=ClientContextResponse)
async def get_client_context(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> ClientContextResponse:
    """
    Get client context profile by client_id.

    Args:
        client_id: Client UUID
        authorization: JWT bearer token

    Returns:
        ClientContextResponse with context data

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to access another client's context
        HTTPException 404: Context not found for this client
        HTTPException 500: Database or unexpected error

    Security:
        Verifies authenticated client_id matches requested client_id
    """
    try:
        # Verify client is accessing their own context
        authenticated_client_id = await get_current_user_id(authorization)
        if authenticated_client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access another client's context"
            )

        # Retrieve context from database
        context_data = await context_repository.get_client_context(client_id)

        # Return 404 if not found (NOT 200 with data=None)
        if not context_data:
            raise HTTPException(
                status_code=404,
                detail="Context not found for this client"
            )

        logger.info(f"Context retrieved for client {client_id}")
        return ClientContextResponse(
            success=True,
            data=ClientContextData(**context_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving client context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving context"
        )
