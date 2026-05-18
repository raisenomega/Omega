"""
Context Creation Endpoint
Handles client context profile creation
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from datetime import datetime, timezone

from app.api.routes.context.models import (
    ClientContextCreate,
    ClientContextResponse,
    ClientContextData
)
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.repositories.context_repository import context_repository

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ClientContextResponse)
async def create_client_context(
    request: ClientContextCreate,
    authorization: Optional[str] = Header(None)
) -> ClientContextResponse:
    """
    Create new client context profile.

    Args:
        request: Context creation payload
        authorization: JWT bearer token

    Returns:
        ClientContextResponse with created context data

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to create context for another client
        HTTPException 409: Context already exists for this client
        HTTPException 500: Database or unexpected error

    Security:
        Verifies authenticated client_id matches requested client_id
    """
    try:
        # Verify client is creating their own context
        authenticated_client_id = await get_current_user_id(authorization)
        if authenticated_client_id != request.client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot create context for another client"
            )

        # Check if context already exists
        existing_context = await context_repository.get_client_context(
            request.client_id
        )
        if existing_context:
            raise HTTPException(
                status_code=409,
                detail="Context already exists for this client. Use PATCH to update."
            )

        # Prepare context data with metadata
        context_data = request.model_dump()
        context_data["version"] = 1
        context_data["is_active"] = True
        context_data["created_at"] = datetime.now(timezone.utc).isoformat()
        context_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Create context in database
        created_context = await context_repository.create_client_context(
            context_data
        )

        logger.info(f"Context created for client {request.client_id}")
        return ClientContextResponse(
            success=True,
            data=ClientContextData(**created_context),
            message="Context profile created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client context: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating context"
        )
