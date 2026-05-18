"""Handlers for Social Account With Context endpoints"""
from fastapi import HTTPException
from typing import Optional
import logging
from datetime import datetime, timezone

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.repositories.client_repository import client_repository
from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.social_accounts.models import SocialAccountProfile, SocialAccountResponse
from .with_context_models import (
    SocialAccountWithContextCreate, SocialAccountWithContextUpdate, PLAN_LIMITS,
)

logger = logging.getLogger(__name__)


def _get_or_create_context(supabase, client_id: str, context_data: dict) -> str:
    existing = supabase.client.table("client_context").select("id")\
        .eq("client_id", client_id).eq("is_active", True).execute()
    if existing.data:
        return existing.data[0]["id"]
    now = datetime.now(timezone.utc).isoformat()
    payload = {**context_data, "client_id": client_id, "target_audience": {},
               "platforms": [], "version": 1, "is_active": True,
               "ai_generated_brief": None, "created_at": now, "updated_at": now}
    result = supabase.client.table("client_context").insert(payload).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create context")
    return result.data[0]["id"]


def _get_context_by_id(supabase, context_id: str) -> Optional[dict]:
    result = supabase.client.table("client_context").select("*")\
        .eq("id", context_id).execute()
    return result.data[0] if result.data else None


def _update_context_by_id(supabase, context_id: str, updates: dict) -> None:
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = supabase.client.table("client_context").update(updates)\
        .eq("id", context_id).execute()
    if not result.data:
        logger.warning(f"Failed to update context {context_id}")


async def handle_create_with_context(
    request: SocialAccountWithContextCreate,
    authorization: Optional[str],
) -> SocialAccountResponse:
    user = await get_current_user(authorization)
    role, authenticated_id = user["role"], user["id"]
    client = await client_repository.get_client(request.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if role == "reseller" and client.get("reseller_id") != authenticated_id:
        raise HTTPException(status_code=403, detail="Resellers can only create accounts for their clients")
    elif role == "client" and request.client_id != authenticated_id:
        raise HTTPException(status_code=403, detail="Clients can only create accounts for themselves")
    client_plan = client.get("plan", "basic")
    plan_limit = PLAN_LIMITS.get(client_plan, 2)
    existing = await social_account_repository.list_accounts(client_id=request.client_id)
    if len([a for a in existing if a.get("is_active", True)]) >= plan_limit:
        raise HTTPException(status_code=403, detail=(
            f"Plan limit reached. {client_plan.capitalize()} plan allows "
            f"up to {int(plan_limit)} social account(s)."
        ))
    supabase = get_supabase_service()
    context_id = _get_or_create_context(supabase, request.client_id, request.context.model_dump())
    now = datetime.now(timezone.utc).isoformat()
    account_data = {
        "client_id": request.client_id, "platform": request.platform,
        "username": request.username, "profile_url": request.profile_url,
        "context_id": context_id, "scraping_enabled": True,
        "scraped_data": {}, "is_active": True, "created_at": now, "updated_at": now,
    }
    created = await social_account_repository.create_account(account_data)
    logger.info(f"Account with context created: {request.platform} for client {request.client_id}")
    return SocialAccountResponse(success=True, data=SocialAccountProfile(**created),
                                 message="Social account with context created successfully")


async def handle_get_with_context(account_id: str, authorization: Optional[str]) -> dict:
    user = await get_current_user(authorization)
    role, authenticated_id = user["role"], user["id"]
    account = await social_account_repository.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    client_id = account.get("client_id")
    client = await client_repository.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if role == "reseller" and client.get("reseller_id") != authenticated_id:
        raise HTTPException(status_code=403, detail="Resellers can only access their clients' accounts")
    elif role == "client" and client_id != authenticated_id:
        raise HTTPException(status_code=403, detail="Clients can only access their own accounts")
    context = _get_context_by_id(get_supabase_service(), account["context_id"]) \
        if account.get("context_id") else None
    return {"success": True, "data": {**account, "context": context},
            "message": "Account with context retrieved successfully"}


async def handle_update_with_context(
    account_id: str,
    request: SocialAccountWithContextUpdate,
    authorization: Optional[str],
) -> SocialAccountResponse:
    user = await get_current_user(authorization)
    role, authenticated_id = user["role"], user["id"]
    account = await social_account_repository.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    client_id = account.get("client_id")
    client = await client_repository.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if role == "client":
        raise HTTPException(status_code=403, detail="Clients cannot update social accounts")
    elif role == "reseller" and client.get("reseller_id") != authenticated_id:
        raise HTTPException(status_code=403, detail="Resellers can only update their clients' accounts")
    if request.context and account.get("context_id"):
        _update_context_by_id(get_supabase_service(), account["context_id"], request.context.model_dump())
    account_updates = {}
    if request.username is not None:
        account_updates["username"] = request.username
    if request.profile_url is not None:
        account_updates["profile_url"] = request.profile_url
    updated = await social_account_repository.update_account(account_id, account_updates) \
        if account_updates else account
    logger.info(f"Social account {account_id} updated")
    return SocialAccountResponse(success=True, data=SocialAccountProfile(**updated),
                                 message="Social account updated successfully")
