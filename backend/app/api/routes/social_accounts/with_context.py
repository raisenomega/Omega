"""Social Account With Context — Router (thin orchestrator)
POST  /social-accounts/with-context/            - Create account + context
GET   /social-accounts/with-context/{id}/       - Get account + context hydrated
PATCH /social-accounts/with-context/{id}/       - Update account + context
"""
from fastapi import APIRouter, Header
from typing import Optional
from app.api.routes.social_accounts.models import SocialAccountResponse
from .with_context_models import SocialAccountWithContextCreate, SocialAccountWithContextUpdate
from .with_context_handlers import (
    handle_create_with_context,
    handle_get_with_context,
    handle_update_with_context,
)

router = APIRouter()


@router.post("/", response_model=SocialAccountResponse)
async def create_account_with_context(
    request: SocialAccountWithContextCreate,
    authorization: Optional[str] = Header(None),
) -> SocialAccountResponse:
    """Create social account with its own context in one operation."""
    return await handle_create_with_context(request, authorization)


@router.get("/{account_id}/")
async def get_account_with_context(
    account_id: str,
    authorization: Optional[str] = Header(None),
):
    """Get social account with its full context hydrated."""
    return await handle_get_with_context(account_id, authorization)


@router.patch("/{account_id}/", response_model=SocialAccountResponse)
async def update_account_with_context(
    account_id: str,
    request: SocialAccountWithContextUpdate,
    authorization: Optional[str] = Header(None),
) -> SocialAccountResponse:
    """Update social account and optionally its context."""
    return await handle_update_with_context(account_id, request, authorization)
