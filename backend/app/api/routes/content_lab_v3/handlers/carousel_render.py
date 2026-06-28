"""POST /content-lab/carousel-render · A2.4 · ensambla el guion (editado en el front) → N placas reales.

Cierre del backend de Pieza 1. Ensambla las 5 piezas: A2.3 (pre-check N) → A2.1 (marca) → ensamblado
Q1-A → A2.2 (paralelo todo-o-nada) → persist 1 draft con media_urls de N → débito N×costo atómico.
NO regenera el guion (no llama A1.2/RAFA) · NO toca credits_service · NO toca Pieza 2 (el agendar ya
lee media_urls). Sync (rate limit medido 10s). F1: el guion fue gratis · el cobro es solo aquí.
"""
import asyncio
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3._brand_prompt import fetch_brand_block
from app.api.routes.content_lab_v3._carousel_render import build_placa_prompts
from app.api.routes.content_lab_v3._carousel_logo import apply_logo_to_urls
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateCarouselRenderRequest, GenerateCarouselRenderResponse,
)
from app.bc_cognition.infrastructure._carousel_images import generate_carousel_images
from app.bc_cognition.infrastructure._storage_uploader import StorageUploadError
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction
from app.bc_billing.application.credits_service import check_budget_for_n, debit
from app.bc_billing.domain.credit_costs import cost_for_image

router = APIRouter()


def _clean_or_400(text: str) -> str:
    """F2 · sanitiza un campo del slide (viene editable del front). BLOCK/HOLD → 400."""
    si, serr = sanitize_input(text, InputContext.CONTENT_PROMPT)
    if serr is not None or si is None or si.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        raise HTTPException(status_code=400, detail="unsafe_input:slide")
    return si.clean_text


@router.post("/carousel-render", response_model=GenerateCarouselRenderResponse)
async def carousel_render(
    request: GenerateCarouselRenderRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateCarouselRenderResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])
    n = len(request.slides)

    if not await check_budget_for_n(client_id, n):  # A2.3 · pre-check N (80% colchón) ANTES de generar
        raise HTTPException(status_code=402, detail="credits_exhausted")

    clean = [s.model_copy(update={"text": _clean_or_400(s.text), "visual_note": _clean_or_400(s.visual_note)})
             for s in request.slides]
    brand = await fetch_brand_block(client_id)  # A2.1 · 1 vez · misma marca para las N
    prompts = build_placa_prompts(clean, brand)

    try:
        urls = await generate_carousel_images(prompts, client_id=client_id, size="1024x1280")  # A2.2 · 4:5 · todo-o-nada
    except StorageUploadError as e:
        raise HTTPException(status_code=502, detail=f"storage_upload_error:{e}")
    except Exception as e:  # A2.2 lanzó (1 placa falló) → propaga → 0 persist, 0 débito
        if "rate_limited" in str(e):
            raise HTTPException(status_code=429, detail="image_gen_rate_limited", headers={"Retry-After": "30"})
        raise HTTPException(status_code=503, detail=f"carousel_render_error:{e}")
    if not urls:
        raise HTTPException(status_code=503, detail="carousel_render_empty")

    # Commit A · overlay opt-in del logo (paridad imagen suelta) · POST-generación · best-effort por placa.
    # find_client_logo_url (DB sync) en to_thread. Sin logo del cliente → placas sin logo, sin error.
    if request.apply_logo:
        logo_url = await asyncio.to_thread(repo.find_client_logo_url, client_id)
        if logo_url:
            urls = await apply_logo_to_urls(urls, logo_url, client_id)

    content_id = await repo.safe_insert(
        "insert_carousel", repo.insert_generated_content, client_id, {
            "agent_code": "content_creator", "content_type": "carousel",
            "generated_text": request.carousel_title, "media_urls": urls,  # E5 · jsonb · Pieza 2 lo agenda
            "metadata": {"model": "nano-banana-2", "provider": "google", "ui_type": "carousel",
                         "slides": [s.model_dump() for s in clean]},  # F4 · el guion (front renderiza + re-edita)
            "confidence": 8, "status": "draft", "compliance_passed": True,
        },
    )
    if content_id:  # F1 · débito N×costo atómico DESPUÉS del persist exitoso (cierra DEBT-A12 · guion gratis)
        await debit(client_id, "content_creator", n * cost_for_image("default"), "nano-banana", content_id)
    return GenerateCarouselRenderResponse(
        id=content_id or "", content_type="carousel",
        carousel_title=request.carousel_title, media_urls=urls,
    )
