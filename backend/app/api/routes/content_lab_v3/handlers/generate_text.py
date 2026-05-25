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
from app.api.routes.content_lab_v3._attachment_extractor import (
    ExtractionError, extract_text,
)
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3._prompt_vault_selector import (
    SafeDict, select_optimal_prompt,
)
from app.api.routes.content_lab_v3.handlers._system_builder import build_rafa_system
from app.api.routes.content_lab_v3.handlers._variations import generate_variations
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateTextRequest, GenerateTextResponse,
)
from app.bc_cognition.application import use_brand_dna
from app.bc_cognition.application.web_context import fetch_web_context
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction

router = APIRouter()

_PRO_PLANS = ("pro", "enterprise")

_INDUSTRY_TO_VERTICAL = {
    "inmobiliaria": "real_estate", "restaurante": "restaurant",
    "salud": "health", "construccion": "construction",
    "tecnologia": "technology", "retail": "retail",
    "educacion": "education", "servicios": "services",
}


@router.post("/generate", response_model=GenerateTextResponse)
async def generate_text(
    request: GenerateTextRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateTextResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])

    # SPRINT 4A-3 #3: sanear topic del usuario (T1/T3 · CONTENT_PROMPT) antes del prompt
    st, serr = sanitize_input(request.topic, InputContext.CONTENT_PROMPT)
    if serr is not None or st is None or st.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        raise HTTPException(status_code=400, detail="unsafe_input:topic")
    request.topic = st.clean_text

    if request.variations > 1 and repo.find_client_plan(client_id) not in _PRO_PLANS:
        raise HTTPException(status_code=403, detail="variations_require_pro_plan")

    ctx = repo.find_client_context(client_id)
    industry = (client.get("industry") or "").lower()
    vertical = _INDUSTRY_TO_VERTICAL.get(industry, "general")
    # DEBT-CL-019: pasar vertical al DNA · si corpus vacío usa industry defaults
    dna = use_brand_dna.build_dna_for_client(client_id, vertical=vertical)
    system = build_rafa_system(
        client, ctx, dna, request.platform, request.content_type, request.tone,
    )
    # DEBT-CL-020: inyectar texto extraído del attachment al system prompt
    if request.reference_attachment_b64 and request.reference_mime_type:
        try:
            extracted = extract_text(request.reference_attachment_b64, request.reference_mime_type)
        except ExtractionError as e:
            raise HTTPException(status_code=400, detail=f"attachment_extract_failed:{e}")
        if extracted:
            system = f"{system}\n\nCONTEXTO ADJUNTO DEL CLIENTE:\n{extracted}"
    # COMMIT 2: auto-Brave-Search · si el topic pide info actual → snippets web saneados (T2)
    web_block = await fetch_web_context(request.topic, vertical, "content_creator", client_id)
    if web_block:
        system = f"{system}\n\n{web_block}"
    vault_prompt = select_optimal_prompt(vertical, request.platform, request.content_type)
    user_message = vault_prompt.format_map(SafeDict(
        client_name=client.get("name", "el cliente"), tone=request.tone,
        target_audience=ctx.get("target_audience", "audiencia general"),
        niche=client.get("niche", ""), region=client.get("region", ""),
        brand_voice=", ".join(dna.tone) if dna.tone else "profesional",
    )) if vault_prompt else f"Tema: {request.topic}"
    n = 3 if request.variations > 1 else 1
    variations = await generate_variations(system, request, dna, client_id, n, user_message)
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
