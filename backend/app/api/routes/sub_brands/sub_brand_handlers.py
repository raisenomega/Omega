"""Handlers for sub-brands endpoints."""
from typing import Optional
from datetime import datetime, timezone
from fastapi import HTTPException, Header
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service
from .sub_brand_models import SubBrandCreate, SubBrandListResponse, SubBrandResponse


async def get_sub_brands(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> SubBrandListResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    # RBAC check
    role = user.get("role")
    if role == "client" and user.get("id") != client_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    if role == "reseller":
        client_row = supabase.client.table("clients").select("reseller_id").eq("id", client_id).single().execute()
        if not client_row.data or client_row.data.get("reseller_id") != user.get("id"):
            raise HTTPException(status_code=403, detail="Acceso denegado")

    result = supabase.client.table("sub_brands").select("*").eq("client_id", client_id).eq("is_active", True).execute()
    brands = result.data or []
    return SubBrandListResponse(success=True, data=brands, total=len(brands))


async def create_sub_brand(
    client_id: str,
    payload: SubBrandCreate,
    authorization: Optional[str] = Header(None),
) -> SubBrandResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    # RBAC check
    role = user.get("role")
    if role == "client" and user.get("id") != client_id:
        raise HTTPException(status_code=403, detail="Acceso denegado")
    if role == "reseller":
        client_row = supabase.client.table("clients").select("reseller_id").eq("id", client_id).single().execute()
        if not client_row.data or client_row.data.get("reseller_id") != user.get("id"):
            raise HTTPException(status_code=403, detail="Acceso denegado")

    now = datetime.now(timezone.utc).isoformat()
    brand_id = str(int(datetime.now(timezone.utc).timestamp() * 1000))

    new_brand = {
        "id": brand_id,
        "client_id": client_id,
        "name": payload.name,
        "description": payload.description,
        "logo_url": payload.logo_url,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    result = supabase.client.table("sub_brands").insert(new_brand).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Error al crear la marca")

    return SubBrandResponse(success=True, data=result.data[0])
