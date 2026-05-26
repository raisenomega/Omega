"""POST /api/v1/content-lab/generate-image · genera imagen via _image_compat.

DDD A1/A9: handler -> repo + _image_compat (sube a Storage · DEBT-018 cerrada).
Sin Brand DNA en esta versión · scope quirúrgico Paso 4 (puede agregarse en
futuro augmentando el prompt con visual_style del DNA).
Error semantics: 502 si falla upload a Storage · 503 si falla Nano Banana.
"""
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._attachment_extractor import (
    ExtractionError, extract_text,
)
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateImageRequest, GenerateImageResponse,
)
from app.bc_cognition.infrastructure._image_compat import generate_image_compat
from app.bc_cognition.infrastructure._storage_uploader import StorageUploadError, upload_image_bytes
from app.bc_cognition.infrastructure._logo_overlay import overlay_logo

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


@router.post("/generate-image", response_model=GenerateImageResponse)
async def generate_image(
    request: GenerateImageRequest,
    authorization: Optional[str] = Header(None),
) -> GenerateImageResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])

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

    content_id = repo.safe_insert(
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
    return GenerateImageResponse(
        id=content_id or "", content_type="image", generated_text=image_url,
    )
