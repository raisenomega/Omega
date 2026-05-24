"""POST /api/v1/content-lab/generate-image · genera imagen via _image_compat.

DDD A1/A9: handler -> repo + _image_compat (sube a Storage · DEBT-018 cerrada).
Sin Brand DNA en esta versión · scope quirúrgico Paso 4 (puede agregarse en
futuro augmentando el prompt con visual_style del DNA).
Error semantics: 502 si falla upload a Storage · 503 si falla Nano Banana.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateImageRequest, GenerateImageResponse,
)
from app.bc_cognition.infrastructure._image_compat import generate_image_compat
from app.bc_cognition.infrastructure._storage_uploader import StorageUploadError

router = APIRouter()

_STYLE_SUFFIXES = {
    "realistic": ", photorealistic, high quality, professional photography",
    "cartoon": ", cartoon style, vibrant colors, playful illustration",
    "minimal": ", minimalist design, clean lines, simple composition",
}

# UX-3 · aspect ratio → resolution (compat con _SIZE_TO_ASPECT en _image_compat)
# OJO DEBT-CL-011: nano_banana_adapter recibe aspect pero NO lo pasa al SDK
# todavía (ImageConfig pendiente en google-genai 2.6 · verificación SDK aparte).
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
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    enhanced = _enhance_prompt(request.prompt, request.style)
    size = _ASPECT_TO_SIZE.get(request.aspect_ratio, "1024x1024")
    try:
        urls = await generate_image_compat(
            prompt=enhanced, n=1, size=size,
            quality="standard", client_id=client_id,
        )
    except StorageUploadError as e:
        raise HTTPException(status_code=502, detail=f"storage_upload_error:{e}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"image_gen_error:{e}")
    if not urls:
        raise HTTPException(status_code=503, detail="image_gen_empty")
    image_url = urls[0]

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
