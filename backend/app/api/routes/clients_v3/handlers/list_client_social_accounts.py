"""GET /api/v1/clients/{client_id}/social-accounts · DEBT-CL-015.

Lista cuentas sociales del cliente · auth + ownership · solo cols seguras
(id + platform + account_name + status · cero tokens). Filter opcional por
platform.

Frontend `useMyAccounts(clientId, platform)` consume este endpoint para
poblar el dropdown del form bar cuando el cliente tiene 2+ cuentas para
la platform seleccionada.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3.models.social_accounts import (
    SocialAccountListResponse, SocialAccountSummary,
)
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.get(
    "/{client_id}/social-accounts",
    response_model=SocialAccountListResponse,
)
async def list_client_social_accounts(
    client_id: str,
    platform: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
) -> SocialAccountListResponse:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="client_access_denied")
    sb = get_supabase_service().client
    q = sb.table("social_accounts").select(
        "id, platform, account_name, status",
    ).eq("client_id", client_id).eq("status", "active").order("created_at")
    if platform:
        q = q.eq("platform", platform)
    rows = q.execute().data or []
    items = [SocialAccountSummary(**r) for r in rows]
    return SocialAccountListResponse(items=items, total=len(items))
