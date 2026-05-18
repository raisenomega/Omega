"""
Social Account Update Endpoint
PATCH /social-accounts/{account_id} - Update social account
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.social_accounts.models import (
    SocialAccountUpdate,
    SocialAccountResponse,
    SocialAccountProfile
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.patch("/{account_id}", response_model=SocialAccountResponse)
async def update_social_account(
    account_id: str,
    request: SocialAccountUpdate,
    authorization: Optional[str] = Header(None)
) -> SocialAccountResponse:
    """
    Update social account fields.
    Only owner and reseller can update. Clients cannot modify.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Verify account exists
        account = await social_account_repository.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")

        # 3. Verify access to the client
        client_id = account.get("client_id")
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 4. Role-based access control
        if role == "client":
            raise HTTPException(
                status_code=403,
                detail="Clients cannot update social accounts. Contact your reseller."
            )
        elif role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only update their clients' accounts"
            )

        # 5. Build update data (only non-None fields)
        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No fields provided for update"
            )

        # 6. Update account
        updated_account = await social_account_repository.update_account(
            account_id, update_data
        )

        logger.info(
            f"Social account {account_id} updated by {role} {authenticated_id}"
        )

        return SocialAccountResponse(
            success=True,
            data=SocialAccountProfile(**updated_account),
            message="Social account updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating social account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while updating social account"
        )
