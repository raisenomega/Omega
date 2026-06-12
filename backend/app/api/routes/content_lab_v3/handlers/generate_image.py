"""POST /api/v1/content-lab/generate-image · genera imagen via _image_compat.

DDD A1/A9: handler -> repo + _image_compat (sube a Storage · DEBT-018 cerrada).
Sin Brand DNA en esta versión · scope quirúrgico Paso 4 (puede agregarse en
futuro augmentando el prompt con visual_style del DNA).
Error semantics: 502 si falla upload a Storage · 503 si falla Nano Banana.
"""
import asyncio
import logging
from typing import Optional, Union
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._attachment_extractor import (
    ExtractionError, extract_text,
)
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateImageRequest, GenerateImageResponse, ImageJobStartResponse, ImageJobStatusResponse,
)
from app.api.routes.clients_v3 import _clients_reader as clients_reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.bc_cognition.infrastructure._image_compat import generate_image_compat
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction
from app.bc_cognition.infrastructure._storage_uploader import StorageUploadError, upload_image_bytes
from app.bc_cognition.infrastructure._logo_overlay import overlay_logo
from app.bc_cognition.application.use_image_job import create_image_job, get_image_job
from app.bc_billing.application.credits_service import check_budget, debit
from app.bc_billing.domain.credit_costs import cost_for_image
from app.feature_flags import get_feature_flags

_IMAGE_PROMPT_MAX = 6000  # truncate attachment context · Nano Banana cap 8000 total

router = APIRouter()
logger = logging.getLogger(__name__)

_STYLE_SUFFIXES = {
    "realistic": ", photorealistic, high quality, professional photography",
    "cartoon": ", cartoon style, vibrant colors, playful illustration",
    "minimal": ", minimalist design, clean lines, simple composition",
}

# UX-3 · aspect ratio → resolution (compat con _SIZE_TO_ASPECT en _image_compat).
# DEBT-CL-011 cerrada Sprint 3: nano_banana_adapter ya pasa aspect_ratio al SDK
# vía ImageConfig (google-genai 2.6) · aspect respetado end-to-end.
_ASPECT_TO_SIZE = {"1:1": "1024x1024", "9:16": "1024x1792", "16:9": "1792x1024"}


def _enhance_prompt(prompt: str, style: str) -> str:
    suffix = _STYLE_SUFFIXES.get(style, _STYLE_SUFFIXES["realistic"])
    enhanced = f"{prompt}{suffix}"
    return enhanced[:8000] if len(enhanced) > 8000 else enhanced


@router.post("/generate-image", response_model=Union[GenerateImageResponse, ImageJobStartResponse])
async def generate_image(
    request: GenerateImageRequest,
    authorization: Optional[str] = Header(None),
) -> Union[GenerateImageResponse, ImageJobStartResponse]:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])

    # DEBT-052: hard block si el budget prepagado está agotado (402)
    if not await check_budget(client_id):
        raise HTTPException(status_code=402, detail="credits_exhausted")

    # Input Sanitizer (T1/T3 · CONTENT_PROMPT · spec PROTOCOLO_SEGURIDAD_INPUT_OMEGA §6)
    si, serr = sanitize_input(request.prompt, InputContext.CONTENT_PROMPT)
    if serr is not None or si is None or si.action in (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW):
        raise HTTPException(status_code=400, detail="unsafe_input:prompt")
    request.prompt = si.clean_text

    enhanced = _enhance_prompt(request.prompt, request.style)
    # DEBT-CL-020: si attachment text → append al prompt como contexto adicional
    if request.reference_attachment_b64 and request.reference_mime_type:
        try:
            extracted = extract_text(request.reference_attachment_b64, request.reference_mime_type)
        except ExtractionError as e:
            raise HTTPException(status_code=400, detail=f"attachment_extract_failed:{e}")
        if extracted:
            truncated = extracted[:_IMAGE_PROMPT_MAX]
            enhanced = f"{enhanced}\n\nCONTEXT FROM USER ATTACHMENT:\n{truncated}"
    size = _ASPECT_TO_SIZE.get(request.aspect_ratio, "1024x1024")
    refs = [request.reference_image_b64] if request.reference_image_b64 else None  # UX-6

    # DEBT-IMAGE-ASYNC F3 · flag ON → job async (worker debita en 'completed') · return ANTES del
    # débito síncrono (doble cobro imposible). Flag OFF (default) → sigue el path síncrono de abajo INTACTO.
    if get_feature_flags().image_async_enabled:
        job_id = await create_image_job(client_id, enhanced, size, "standard",
                                        request.style, request.apply_logo, refs)
        return ImageJobStartResponse(job_id=job_id, status="pending")

    try:
        urls = await generate_image_compat(
            prompt=enhanced, n=1, size=size,
            quality="standard", client_id=client_id,
            reference_images_b64=refs,
        )
    except StorageUploadError as e:
        raise HTTPException(status_code=502, detail=f"storage_upload_error:{e}")
    except Exception as e:
        # DEBT-071: cuota de Google (rate_limited) → 429 + Retry-After en vez de 503 opaco.
        if "rate_limited" in str(e):
            raise HTTPException(status_code=429, detail="image_gen_rate_limited", headers={"Retry-After": "30"})
        raise HTTPException(status_code=503, detail=f"image_gen_error:{e}")
    if not urls:
        raise HTTPException(status_code=503, detail="image_gen_empty")
    image_url = urls[0]
    # Fase 1: overlay opt-in del logo del cliente · best-effort (nunca rompe la generación).
    # DEBT-068 follow-up: find_client_logo_url (DB sync) + overlay_logo (2× httpx + Pillow sync)
    # corren en to_thread → la ruta apply_logo tampoco bloquea el event loop.
    if request.apply_logo:
        logo_url = await asyncio.to_thread(repo.find_client_logo_url, client_id)
        if logo_url:
            try:
                overlaid = await asyncio.to_thread(overlay_logo, image_url, logo_url)
                image_url = await upload_image_bytes(overlaid, "image/png", client_id)
            except Exception as e:
                logger.warning(f"logo overlay falló · imagen sin marca · client={client_id}: {e}")

    content_id = await repo.safe_insert(
        "insert_image", repo.insert_generated_content, client_id, {
            "agent_code": "content_creator", "content_type": "image",
            "prompt": request.prompt, "generated_text": image_url,
            "metadata": {
                "model": "nano-banana-2", "provider": "google",
                "style": request.style, "ui_type": "image",
            },
            "confidence": 8, "status": "draft", "compliance_passed": True,
        },
    )
    if content_id:
        # DEBT-052: debita el costo de imagen (Nano Banana · §4.4) al cliente enrolado
        await debit(client_id, "content_creator", cost_for_image("default"), "nano-banana", content_id)
    return GenerateImageResponse(
        id=content_id or "", content_type="image", generated_text=image_url,
    )


@router.get("/generate-image/{job_id}", response_model=ImageJobStatusResponse)
async def get_image_job_status(
    job_id: str,
    authorization: Optional[str] = Header(None),
) -> ImageJobStatusResponse:
    """DEBT-IMAGE-ASYNC F3 · estado del job async. 404-no-leak (patrón video · P2):
    job inexistente O de otro cliente → 404 (no revela existencia de jobs ajenos)."""
    user = await get_current_user(authorization)
    job = get_image_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    job_client = clients_reader.get_client(str(job.get("client_id") or ""))
    if not job_client or not user_owns_client(user["id"], job_client):
        raise HTTPException(status_code=404, detail="job_not_found")  # no leak (P2)
    return ImageJobStatusResponse(
        job_id=job_id, status=job["status"],
        image_url=job.get("image_url"), error=job.get("error"),
        content_id=(job.get("metadata") or {}).get("content_id"),
    )
