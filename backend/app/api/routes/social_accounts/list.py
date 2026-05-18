"""
Social Accounts List Endpoint
GET /social-accounts?client_id={id}&platform={platform}
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
import logging

from app.api.routes.social_accounts.models import (
    SocialAccountListResponse,
    SocialAccountProfile,
    PlatformOption
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=SocialAccountListResponse)
async def list_social_accounts(
    client_id: str = Query(..., description="Client UUID"),
    platform: Optional[PlatformOption] = Query(None, description="Filter by platform"),
    authorization: Optional[str] = Header(None)
) -> SocialAccountListResponse:
    """
    List social accounts for a client.
    Requires authentication. Returns accounts filtered by client_id and optional platform.
    """
    try:
        # 1. Get authenticated user with role
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Verify client exists and user has access
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 3. Role-based access control
        if role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only access their own clients"
            )
        elif role == "client" and client_id != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Clients can only access their own accounts"
            )

        # 4. List accounts
        accounts_data = await social_account_repository.list_accounts(
            client_id=client_id,
            platform=platform
        )

        accounts = [SocialAccountProfile(**account) for account in accounts_data]

        return SocialAccountListResponse(
            success=True,
            data=accounts,
            total=len(accounts),
            message=f"Found {len(accounts)} social account(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing social accounts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while listing social accounts"
        )
