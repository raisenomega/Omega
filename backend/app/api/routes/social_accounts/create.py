"""
Social Account Create Endpoint
POST /social-accounts/ - Create new social account
"""
from fastapi import APIRouter, HTTPException, Header, Query, Body
from typing import Optional
import logging
from datetime import datetime, timezone

from app.api.routes.social_accounts.models import (
    SocialAccountCreate,
    SocialAccountResponse,
    SocialAccountProfile
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()

# Plan limits for social accounts
PLAN_LIMITS = {
    "basic": 2,
    "pro": 5,
    "enterprise": float('inf')  # Unlimited
}


@router.post("/", response_model=SocialAccountResponse)
async def create_social_account(
    request: SocialAccountCreate,
    authorization: Optional[str] = Header(None)
) -> SocialAccountResponse:
    """
    Create new social account for a client.
    Validates plan limits: Basic (2), Pro (5), Enterprise (unlimited).
    """
    try:
        # 1. Get authenticated user with role
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Extract client_id from request body
        client_id = request.client_id

        # 3. Verify client exists and user has access
        client = await client_repository.get_client(client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        # 3. Role-based access control
        if role == "reseller" and client.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only create accounts for their clients"
            )
        elif role == "client" and client_id != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Clients can only create accounts for themselves"
            )

        # 4. Validate plan limits
        client_plan = client.get("plan", "basic")
        plan_limit = PLAN_LIMITS.get(client_plan, 2)

        # Count existing active accounts for this client
        existing_accounts = await social_account_repository.list_accounts(
            client_id=client_id
        )
        active_count = len([acc for acc in existing_accounts if acc.get("is_active", True)])

        if active_count >= plan_limit:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Plan limit reached. {client_plan.capitalize()} plan allows "
                    f"up to {int(plan_limit)} social account(s). "
                    f"Upgrade to add more accounts."
                )
            )

        # 5. Build account data
        account_data = {
            "client_id": client_id,
            "platform": request.platform,
            "username": request.username,
            "profile_url": request.profile_url,
            "context_id": request.context_id,
            "scraping_enabled": True,
            "scraped_data": {},
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 6. Create account in database
        created_account = await social_account_repository.create_account(account_data)

        logger.info(
            f"Social account created: {request.platform} - {request.username} "
            f"for client {client_id} by {role} {authenticated_id}"
        )

        return SocialAccountResponse(
            success=True,
            data=SocialAccountProfile(**created_account),
            message="Social account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating social account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating social account"
        )
