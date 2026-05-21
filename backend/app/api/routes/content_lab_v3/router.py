"""Main router content_lab_v3 · /content-lab prefix."""
from fastapi import APIRouter
from app.api.routes.content_lab_v3.handlers.generate_text import router as gen_router

router = APIRouter(prefix="/content-lab", tags=["Content Lab V3"])
router.include_router(gen_router)
