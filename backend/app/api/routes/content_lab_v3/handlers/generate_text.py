"""POST /api/v1/content-lab/generate · genera texto via anthropic_adapter.

DDD A1/A9: handler -> repo + anthropic_adapter (ÚNICO entry I1).
Wired: RAFA persona (T2 S1) + Brand DNA (T3 S1) + Virality V1 (P3 S2) + A/B variations (P2 S2).
Plan PRO/enterprise desbloquea variations=3 · default 1. 403 variations_require_pro_plan si no.
Insert con status='draft' · compliance_passed=True · confidence=8.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.handlers._system_builder import build_rafa_system
from app.api.routes.content_lab_v3.handlers._variations import generate_variations
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateTextRequest, GenerateTextResponse,
)
from app.bc_cognition.application import use_brand_dna

router = APIRouter()

_PRO_PLANS = ("pro", "enterprise")


@router.post("/generate", response_model=GenerateTextResponse)
async def generate_text(
    request: GenerateTextRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateTextResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    if request.variations > 1 and repo.find_client_plan(client_id) not in _PRO_PLANS:
        raise HTTPException(status_code=403, detail="variations_require_pro_plan")

    ctx = repo.find_client_context(client_id)
    dna = use_brand_dna.build_dna_for_client(client_id)
    system = build_rafa_system(
        client, ctx, dna, request.platform, request.content_type, request.tone,
    )
    n = 3 if request.variations > 1 else 1
    variations = await generate_variations(system, request, dna, client_id, n)
    if not variations:
        raise HTTPException(status_code=503, detail="all_variations_failed")

    first = variations[0]
    return GenerateTextResponse(
        id=first.id, content_type=request.content_type,
        generated_text=first.generated_text,
        virality_score=first.virality_score,
        virality_estimated=first.virality_estimated,
        variations=variations,
    )
