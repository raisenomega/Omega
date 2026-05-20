"""PATCH /api/v1/clients/profile · update name/industry/region.

Valida industry ∈ INDUSTRIES + region ∈ REGIONS (domain constants · A2).
Result-tuple interno (A5) · sin Any (C1) · ≤75L (C4).
"""
from typing import Optional, Tuple
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3.models.client_profile import (
    ClientProfileResponse,
    UpdateClientProfileRequest,
)
from app.domain.client_constants import INDUSTRIES, REGIONS
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


def _validate(req: UpdateClientProfileRequest) -> Tuple[bool, Optional[str]]:
    """Result-tuple (A5): (ok, error_code)."""
    if req.industry is not None and req.industry not in INDUSTRIES:
        return (False, "invalid_industry")
    if req.region is not None and req.region not in REGIONS:
        return (False, "invalid_region")
    if req.name is None and req.industry is None and req.region is None:
        return (False, "empty_payload")
    return (True, None)


@router.patch("/profile", response_model=ClientProfileResponse)
async def update_client_profile(
    request: UpdateClientProfileRequest,
    authorization: Optional[str] = Header(None),
) -> ClientProfileResponse:
    user = await get_current_user(authorization)
    ok, err = _validate(request)
    if not ok:
        raise HTTPException(status_code=422, detail=err)
    patch: dict[str, str] = {}
    if request.name is not None:
        patch["name"] = request.name
    if request.industry is not None:
        patch["industry"] = request.industry
    if request.region is not None:
        patch["region"] = request.region
    supabase = get_supabase_service()
    r = supabase.client.table("clients").update(patch).eq("user_id", user["id"]).execute()
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
