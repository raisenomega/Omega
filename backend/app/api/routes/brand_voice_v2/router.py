"""Main router brand_voice_v2 · /brand-voice prefix."""
from fastapi import APIRouter
from app.api.routes.brand_voice_v2.handlers.get_summary import router as summary_router

router = APIRouter(prefix="/brand-voice", tags=["Brand Voice V2"])
router.include_router(summary_router)
