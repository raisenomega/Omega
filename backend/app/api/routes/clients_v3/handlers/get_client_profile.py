"""GET /api/v1/clients/profile · perfil del cliente del usuario auth.

DDD A1: handler (presentation) · supabase via infrastructure helper.
sin Any (C1) · ≤75L (C4).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3.models.client_profile import ClientProfileResponse
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.get("/profile", response_model=ClientProfileResponse)
async def get_client_profile(
    authorization: Optional[str] = Header(None),
) -> ClientProfileResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()
    r = supabase.client.table("clients").select(
        "id, name, industry, region, aria_level"
    ).eq("user_id", user["id"]).limit(1).execute()
    if not r.data:
        raise HTTPException(status_code=404, detail="client_not_found")
    row = r.data[0]
    return ClientProfileResponse(
        id=row["id"],
        name=row.get("name"),
        industry=row.get("industry"),
        region=row.get("region"),
        aria_level=row.get("aria_level"),
    )
