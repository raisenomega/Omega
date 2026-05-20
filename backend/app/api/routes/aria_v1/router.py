"""Main router de aria_v1 · agrupa message + history + track bajo /aria prefix."""
from fastapi import APIRouter
from app.api.routes.aria_v1.handlers.message import router as message_router
from app.api.routes.aria_v1.handlers.history import router as history_router
from app.api.routes.aria_v1.handlers.track import router as track_router

router = APIRouter(prefix="/aria", tags=["ARIA"])
router.include_router(message_router)
router.include_router(history_router)
router.include_router(track_router)
