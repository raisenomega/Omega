"""
Auth Profile Routes
Endpoints for user profile, logout, and token refresh
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.models.shared_models import APIResponse
from app.api.routes.auth.models import RefreshTokenRequest
from app.api.routes.auth.jwt_utils import (
    get_current_user_id,
    create_access_token,
    verify_refresh_token,
)
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=APIResponse)
async def get_profile(authorization: Optional[str] = Header(None)) -> APIResponse:
    """
    Get current user profile from JWT token

    Args:
        authorization: Authorization header ("Bearer <token>")

    Returns:
        APIResponse with:
            - success: True
            - data: Client object (id, name, email, plan, role, reseller_id, etc.)
            - message: Success message

    Raises:
        HTTPException 401: Missing or invalid authorization header
        HTTPException 404: Client not found
        HTTPException 500: Server error

    Extracts client_id from JWT access token and returns full profile
    """
    try:
        # Extract and verify client_id from token
        client_id = await get_current_user_id(authorization)

        service = get_supabase_service()

        # Query client profile
        client_response = service.client.table("clients")\
            .select("id, name, email, plan, role, reseller_id, status, subscription_status, trial_active, created_at")\
            .eq("id", client_id)\
            .execute()

        if not client_response.data or len(client_response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        client = client_response.data[0]

        return APIResponse(
            success=True,
            data=client,
            message="Profile retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout", response_model=APIResponse)
async def logout(authorization: Optional[str] = Header(None)) -> APIResponse:
    """
    Logout current user

    Args:
        authorization: Authorization header ("Bearer <token>")

    Returns:
        APIResponse with:
            - success: True
            - message: Logout successful

    Raises:
        HTTPException 401: Missing or invalid authorization header
        HTTPException 500: Server error

    Note: JWT tokens are stateless. Logout is handled client-side by
    removing tokens from storage. This endpoint logs the action and
    validates the token before confirming logout.
    """
    try:
        # Verify token is valid
        client_id = await get_current_user_id(authorization)

        logger.info(f"Client logged out: {client_id}")

        return APIResponse(
            success=True,
            message="Logout successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(request: RefreshTokenRequest) -> APIResponse:
    """
    Refresh access token using refresh token

    Args:
        request: RefreshTokenRequest with refresh_token

    Returns:
        APIResponse with:
            - success: True
            - token: New JWT access token (7-day expiration)
            - message: Success message

    Raises:
        HTTPException 401: Invalid or expired refresh token
        HTTPException 404: Client not found
        HTTPException 500: Server error

    Flow:
        1. Verify refresh token and extract client_id
        2. Query client data from database
        3. Generate new access token with current client data
        4. Return new access token
    """
    try:
        # Verify refresh token and extract client_id
        client_id = verify_refresh_token(request.refresh_token)

        service = get_supabase_service()

        # Query client data for new token
        client_response = service.client.table("clients")\
            .select("id, email, role, reseller_id, status")\
            .eq("id", client_id)\
            .execute()

        if not client_response.data or len(client_response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail="Client not found"
            )

        client = client_response.data[0]

        # Check if account is still active
        if client.get("status") != "active":
            raise HTTPException(
                status_code=403,
                detail="Account is inactive. Contact support."
            )

        # Generate new access token with current client data
        access_token = create_access_token({
            "id": client["id"],
            "email": client["email"],
            "role": client.get("role", "client"),
            "reseller_id": client.get("reseller_id"),
        })

        logger.info(f"Access token refreshed for client: {client['email']}")

        return APIResponse(
            success=True,
            token=access_token,
            message="Token refreshed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail=str(e))
