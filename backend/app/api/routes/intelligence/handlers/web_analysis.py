"""GET /api/v1/intelligence/{client_id}/web-analysis · scraping puro + caché 24h.

Auth: get_current_user + resolve_client_or_403 (mismo patrón content_lab_v3).
Honesto (P1): si el cliente no tiene website → analyzed=False + message claro ·
si el scrape falla → analyzed=False + message con el error (nunca 500 opaco).
NO usa Claude (scraping puro).
"""
from typing import Optional

from fastapi import APIRouter, Header

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.intelligence import _intelligence_repository as repo
from app.api.routes.intelligence._web_scraper import analyze_website
from app.api.routes.intelligence.models import WebAnalysisResponse

router = APIRouter()
_SNAPSHOT_TYPE = "web_analysis"


@router.get("/{client_id}/web-analysis", response_model=WebAnalysisResponse)
async def web_analysis(
    client_id: str,
    refresh: bool = False,
    authorization: Optional[str] = Header(None),
) -> WebAnalysisResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id)
    cid = str(client["id"])

    site = repo.get_client_site(cid)
    website = site.get("website")
    if not website:
        return WebAnalysisResponse(
            analyzed=False,
            message="Este cliente no tiene un sitio web configurado en su perfil.",
        )

    if not refresh:
        cached = repo.get_fresh_snapshot(cid, _SNAPSHOT_TYPE)
        if cached:
            return WebAnalysisResponse(
                **cached["payload"], cached=True, analyzed=True,
                generated_at=cached.get("created_at"), score=cached.get("score") or 0,
            )

    result = await analyze_website(website)
    if not result.get("ok"):
        return WebAnalysisResponse(
            url=website, analyzed=False,
            message=f"No pudimos analizar el sitio: {result.get('error')}",
        )

    payload = {
        "url": website,
        "title": result["title"], "meta_description": result["meta_description"],
        "h1": result["h1"], "h2": result["h2"], "h3": result["h3"],
        "keywords": result["keywords"], "recommendations": result["recommendations"],
    }
    repo.save_snapshot(cid, _SNAPSHOT_TYPE, payload=payload, score=result["score"])
    return WebAnalysisResponse(
        **payload, analyzed=True, score=result["score"], cached=False,
    )
