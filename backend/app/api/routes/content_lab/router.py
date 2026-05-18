"""
Router principal de Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query

from .models import GenerateImageRequest
from .handlers import (
    handle_generate_text,
    handle_generate_image,
    handle_generate_video_runway,
)
# handle_generate_video_fal REMOVED in Fase 2 §2.5 (FAL provider eliminated · DDD I1)
from .router_content import content_router

router = APIRouter(prefix="/content-lab", tags=["content-lab"])


@router.post("/generate/text")
async def generate_text(
    account_id: str = Query(...),
    content_type: str = Query(...),
    brief: str = Query(...),
    language: str = Query(default="es"),
    director: str = Query(default="REX"),
):
    return await handle_generate_text(account_id, content_type, brief, language, director)


@router.post("/generate-image/")
async def generate_image(
    request: GenerateImageRequest,
    account_id: str = Query(None),
):
    effective_account_id = request.account_id or account_id
    return await handle_generate_image(
        account_id=effective_account_id,
        prompt=request.effective_prompt,
        style=request.style,
        attachments=request.attachments,
    )


@router.post("/generate-video-runway/")
async def generate_video_runway(
    account_id: str = Query(...),
    prompt: str = Query(...),
    duration: int = Query(default=5),
    style: str = Query(default="realistic"),
):
    return await handle_generate_video_runway(account_id, prompt, duration, style)


# Endpoint /generate-video-fal/ REMOVED in Fase 2 §2.5 (FAL provider eliminated · DDD I1)


@router.get("/providers/")
async def list_providers():
    from app.services.ai_providers import AIProviders
    providers = AIProviders()
    return {
        "directors": providers.list_directors(),
        "default": providers.get_default_director(),
    }


router.include_router(content_router)
