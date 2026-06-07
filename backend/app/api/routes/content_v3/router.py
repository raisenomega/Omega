"""Main router content_v3 · agrupa list + save + supervisado bajo /content prefix."""
from fastapi import APIRouter
from app.api.routes.content_v3.handlers.list_content import router as list_router
from app.api.routes.content_v3.handlers.save_content import router as save_router
from app.api.routes.content_v3.handlers.set_media import router as set_media_router
from app.api.routes.content_v3.handlers.supervisado import router as supervisado_router

router = APIRouter(prefix="/content", tags=["Content V3"])
router.include_router(list_router)
router.include_router(save_router)
router.include_router(set_media_router)
router.include_router(supervisado_router)
