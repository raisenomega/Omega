"""Main router de aria_v1 · agrupa message + history + track + delete + suggestions bajo /aria prefix."""
from fastapi import APIRouter
from app.api.routes.aria_v1.handlers.message import router as message_router
from app.api.routes.aria_v1.handlers.history import router as history_router
from app.api.routes.aria_v1.handlers.track import router as track_router
from app.api.routes.aria_v1.handlers.delete_history import router as delete_router
from app.api.routes.aria_v1.handlers.suggestions_create import router as suggestions_create_router
from app.api.routes.aria_v1.handlers.suggestions_list import router as suggestions_list_router
from app.api.routes.aria_v1.handlers.suggestions_read import router as suggestions_read_router

router = APIRouter(prefix="/aria", tags=["ARIA"])
router.include_router(message_router)
router.include_router(history_router)
router.include_router(track_router)
router.include_router(delete_router)
router.include_router(suggestions_create_router)
router.include_router(suggestions_list_router)
router.include_router(suggestions_read_router)
