"""Main router content_v3 · agrupa list + save bajo /content prefix."""
from fastapi import APIRouter
from app.api.routes.content_v3.handlers.list_content import router as list_router
from app.api.routes.content_v3.handlers.save_content import router as save_router

router = APIRouter(prefix="/content", tags=["Content V3"])
router.include_router(list_router)
router.include_router(save_router)
