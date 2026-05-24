"""Main router content_lab_v3 · /content-lab prefix."""
from fastapi import APIRouter
from app.api.routes.content_lab_v3.handlers.generate_text import router as gen_router
from app.api.routes.content_lab_v3.handlers.generate_image import router as image_router
from app.api.routes.content_lab_v3.handlers.generate_video import router as video_router
from app.api.routes.content_lab_v3.handlers.improve_prompt import router as improve_router
from app.api.routes.content_lab_v3.handlers.research import router as research_router

router = APIRouter(prefix="/content-lab", tags=["Content Lab V3"])
router.include_router(gen_router)
router.include_router(image_router)
router.include_router(video_router)
router.include_router(improve_router)
router.include_router(research_router)
