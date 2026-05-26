"""GET /api/v1/intelligence/{client_id}/geo-check · visibilidad GEO/AEO + caché 24h.

Auth: get_current_user + resolve_client_or_403 (mismo patrón web_analysis).
Honesto (P1): sin industria → analyzed=False + message · si Brave/Claude fallan →
analyzed=False + message con el error (nunca 500 opaco). Usa Brave + Claude (sonnet).
"""
from typing import Optional

from fastapi import APIRouter, Header

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.intelligence import _intelligence_repository as repo
from app.api.routes.intelligence._geo_analyzer import check_geo_visibility
from app.api.routes.intelligence.models import GeoCheckResponse

router = APIRouter()
_SNAPSHOT_TYPE = "geo_check"


@router.get("/{client_id}/geo-check", response_model=GeoCheckResponse)
async def geo_check(
    client_id: str,
    refresh: bool = False,
    authorization: Optional[str] = Header(None),
) -> GeoCheckResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id)
    cid = str(client["id"])

    site = repo.get_client_site(cid)
    if not site.get("industry"):
        return GeoCheckResponse(
            analyzed=False,
            message="Falta la industria del cliente para verificar visibilidad en IA.",
        )

    if not refresh:
        cached = repo.get_fresh_snapshot(cid, _SNAPSHOT_TYPE)
        if cached:
            return GeoCheckResponse(
                **cached["payload"], cached=True, analyzed=True,
                generated_at=cached.get("created_at"),
            )

    result = await check_geo_visibility(
        site["name"], site["industry"], site.get("region", ""), site.get("website"),
    )
    if not result.get("ok"):
        return GeoCheckResponse(
            analyzed=False,
            message=f"No pudimos verificar: {result.get('error')}",
        )

    payload = {
        "status": result["status"], "summary": result["summary"],
        "tips": result["tips"], "queries": result["queries"],
    }
    repo.save_snapshot(cid, _SNAPSHOT_TYPE, payload=payload, score=None)
    return GeoCheckResponse(**payload, analyzed=True, cached=False)
