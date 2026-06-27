"""POST /content-lab/carousel-script · genera el GUION estructurado del carrusel (A1.2 · NO imágenes).

Capa aparte de RAFA · usa tool_choice forzado (A1.1) para garantizar slides[]. El guion entra por su
PROPIO campo `idea` (max 4000) · NO el prompt de imagen (max 2000) → evita el 422. A2 consumirá luego
cada visual_note para generar las N placas (con marca vía A6). Aquí solo se produce el texto.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3._carousel_brain import (
    generate_carousel_script, CarouselScriptError,
)
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateCarouselScriptRequest, GenerateCarouselScriptResponse,
)
from app.bc_billing.application.credits_service import check_budget
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction

router = APIRouter()


@router.post("/carousel-script", response_model=GenerateCarouselScriptResponse)
async def carousel_script(
    request: GenerateCarouselScriptRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateCarouselScriptResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])

    if not await check_budget(client_id):  # DEBT-052 · 1 llamada de texto (barata) · el costo gordo es A2
        raise HTTPException(status_code=402, detail="credits_exhausted")

    # Input Sanitizer (T1/T3 · CONTENT_PROMPT · igual que generate_text/generate_image)
    si, serr = sanitize_input(request.idea, InputContext.CONTENT_PROMPT)
    if serr is not None or si is None or si.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        raise HTTPException(status_code=400, detail="unsafe_input:idea")

    ctx = repo.find_client_context(client_id)  # mismo BC · NO aria_repository (no acoplar)
    ctx = {**ctx, "client_name": client.get("name"), "niche": client.get("niche")}
    if request.tone:
        ctx["tone"] = request.tone

    try:
        script = await generate_carousel_script(si.clean_text, ctx, request.n_slides or 5)
    except CarouselScriptError as e:
        raise HTTPException(status_code=503, detail=f"carousel_script_failed:{e.code}")
    return GenerateCarouselScriptResponse(**script)
