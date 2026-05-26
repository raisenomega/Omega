"""GET /api/v1/intelligence/{client_id}/aeo-check · Answer Engine Optimization + caché 24h.

Auth: get_current_user + resolve_client_or_403 (mismo patrón geo_check).
Honesto (P1): sin industria → analyzed=False + message · si Brave/Claude fallan →
analyzed=False + message con el error (nunca 500 opaco). Brave (retrieval) + Claude.
"""
from typing import Optional

from fastapi import APIRouter, Header

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.intelligence import _intelligence_repository as repo
from app.api.routes.intelligence._aeo_analyzer import check_aeo
from app.api.routes.intelligence.models import AeoCheckResponse

router = APIRouter()
_SNAPSHOT_TYPE = "aeo_check"


@router.get("/{client_id}/aeo-check", response_model=AeoCheckResponse)
async def aeo_check(
    client_id: str,
    refresh: bool = False,
    authorization: Optional[str] = Header(None),
) -> AeoCheckResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id)
    cid = str(client["id"])

    site = repo.get_client_site(cid)
    if not site.get("industry"):
        return AeoCheckResponse(
            analyzed=False,
            message="Falta la industria del cliente para el análisis AEO.",
        )

    if not refresh:
        cached = repo.get_fresh_snapshot(cid, _SNAPSHOT_TYPE)
        if cached:
            return AeoCheckResponse(
                **cached["payload"], cached=True, analyzed=True,
                generated_at=cached.get("created_at"),
            )

    result = await check_aeo(
        site["name"], site["industry"], site.get("region", ""), site.get("website"),
    )
    if not result.get("ok"):
        return AeoCheckResponse(
            analyzed=False,
            message=f"No pudimos analizar: {result.get('error')}",
        )

    payload = {
        "questions": result["questions"], "answered": result["answered"],
        "gaps": result["gaps"], "tips": result["tips"],
    }
    repo.save_snapshot(cid, _SNAPSHOT_TYPE, payload=payload, score=None)
    return AeoCheckResponse(**payload, analyzed=True, cached=False)
