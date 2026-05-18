"""
Social Account Delete Endpoint
DELETE /social-accounts/{account_id} - Soft delete social account
"""
from fastapi import APIRouter, HTTPException, Header, Response
from typing import Optional
import logging

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.delete("/{account_id}", status_code=204)
async def delete_social_account(
    account_id: str,
    authorization: Optional[str] = Header(None)
) -> Response:
    """
    Soft delete social account (is_active = false).
    Only owner can delete.
    """
    try:
        # 1. Get authenticated user
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Only owner can delete
        if role != "owner":
            raise HTTPException(
                status_code=403,
                detail="Only platform owners can delete social accounts"
            )

        # 3. Verify account exists
        account = await social_account_repository.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Social account not found")

        # 4. Soft delete
        success = await social_account_repository.delete_account(account_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete social account"
            )

        logger.info(
            f"Social account {account_id} deleted by owner {authenticated_id}"
        )

        return Response(status_code=204)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting social account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting social account"
        )
