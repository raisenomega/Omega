"""GET /api/v1/brand-voice/summary · read-only summary del corpus del cliente.

DDD A1/A9: handler -> use_case -> repo. Cero acceso Supabase directo.
Sprint 2 ②.A · alimenta página /brand-voice (BrandVoicePage.tsx).
Errores: 403 si user no es cliente · 200 con conteos=0 si corpus vacío.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Query

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.brand_voice_v2.models import (
    BrandVoiceSummaryResponse, CorpusEntry, KeywordCount,
)
from app.api.routes.content_lab_v3 import _content_lab_repository as client_repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_cognition.application.use_brand_voice_summary import (
    build_brand_voice_summary,
)

router = APIRouter()


@router.get("/summary", response_model=BrandVoiceSummaryResponse)
async def get_summary(
    authorization: Optional[str] = Header(None),
    client_id: Optional[str] = Query(None),  # Switcher V1: negocio activo · ausente → legacy LIMIT 1
) -> BrandVoiceSummaryResponse:
    user = await get_current_user(authorization)
    # client_id presente → resolver+validar el negocio activo (403 si ajeno). Ausente → legacy.
    client = resolve_client_or_403(user["id"], client_id) if client_id else client_repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")

    data = build_brand_voice_summary(client_id=str(client["id"]))
    return BrandVoiceSummaryResponse(
        corpus_count=data["corpus_count"],
        latest_approvals=[CorpusEntry(**e) for e in data["latest_approvals"]],
        top_keywords=[KeywordCount(**k) for k in data["top_keywords"]],
    )
