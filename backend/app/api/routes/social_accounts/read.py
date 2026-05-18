"""
Social Account Read Endpoint
GET /social-accounts/{account_id} - Get social account by ID
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.social_accounts.models import (
    SocialAccountResponse,
    SocialAccountProfile
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{account_id}", response_model=SocialAccountResponse)
async def get_social_account(
    account_id: str,
    authorization: Optional[str] = Header(None)
) -> SocialAccountResponse:
    """
    Get social account by ID.
    Requires authentication and proper access rights.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Get account
        account = await social_account_repository.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")

        # 3. Verify access to the client
        client_id = account.get("client_id")
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 4. Role-based access control
        if role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only access their clients' accounts"
            )
        elif role == "client" and client_id != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Clients can only access their own accounts"
            )

        return SocialAccountResponse(
            success=True,
            data=SocialAccountProfile(**account),
            message="Social account retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting social account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving social account"
        )
