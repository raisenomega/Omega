"""Mapeo Zernio per-negocio per-plataforma · F5/2b.

GET    /clients/{id}/zernio-available-accounts?platform=  → cuentas conectadas en Zernio (live).
POST   /clients/{id}/social-accounts/{platform}/zernio      → mapea zernio_account_id al negocio (upsert).
DELETE /clients/{id}/social-accounts/{platform}/zernio      → NULL-ea el mapeo ("Cambiar cuenta" = DELETE→POST).

SEGURIDAD: get_supabase_service usa service_role → BYPASSA RLS. El guard es user_owns_client en CADA
endpoint (igual que list_client_social_accounts) ANTES de tocar social_accounts o Zernio. Sin ese check
un reseller podria modificar cuentas de clientes ajenos.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3.models.social_accounts import (
    ZernioAvailableAccount, ZernioAvailableResponse, ZernioMapRequest,
)
from app.bc_cognition.infrastructure.zernio_adapter import list_accounts
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.get("/{client_id}/zernio-available-accounts", response_model=ZernioAvailableResponse)
async def zernio_available_accounts(
    client_id: str,
    platform: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
) -> ZernioAvailableResponse:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):      # OWNERSHIP GUARD (antes de Zernio)
        raise HTTPException(status_code=403, detail="client_access_denied")
    accounts = await list_accounts()
    items = [
        ZernioAvailableAccount(zernio_account_id=str(a["_id"]),
                               platform=str(a.get("platform") or ""), handle=a.get("name"))
        for a in accounts if a.get("_id") and (not platform or a.get("platform") == platform)
    ]
    return ZernioAvailableResponse(items=items, total=len(items))


@router.post("/{client_id}/social-accounts/{platform}/zernio")
async def map_zernio_account(
    client_id: str, platform: str, body: ZernioMapRequest,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):      # OWNERSHIP GUARD (antes del upsert)
        raise HTTPException(status_code=403, detail="client_access_denied")
    sb = get_supabase_service().client
    existing = (sb.table("social_accounts").select("id")
                .eq("client_id", client_id).eq("platform", platform).limit(1).execute().data)
    payload = {"zernio_account_id": body.zernio_account_id,
               "zernio_account_handle": body.zernio_account_handle,
               "oauth_status": "connected", "status": "active"}
    if existing:
        sb.table("social_accounts").update(payload).eq("id", existing[0]["id"]).execute()
    else:
        sb.table("social_accounts").insert({
            **payload, "client_id": client_id, "platform": platform,
            "account_name": body.zernio_account_handle or body.zernio_account_id,
        }).execute()
    return {"ok": True}


@router.delete("/{client_id}/social-accounts/{platform}/zernio")
async def unmap_zernio_account(
    client_id: str, platform: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):      # OWNERSHIP GUARD (antes del NULL-eo)
        raise HTTPException(status_code=403, detail="client_access_denied")
    sb = get_supabase_service().client
    (sb.table("social_accounts")
     .update({"zernio_account_id": None, "zernio_account_handle": None, "oauth_status": "not_connected"})
     .eq("client_id", client_id).eq("platform", platform).execute())
    return {"ok": True}
