"""Main router clients_v3 · agrupa GET + PATCH bajo /clients prefix."""
from fastapi import APIRouter
from app.api.routes.clients_v3.handlers.get_client_profile import router as get_router
from app.api.routes.clients_v3.handlers.update_client_profile import router as patch_router

router = APIRouter(prefix="/clients", tags=["Clients V3"])
router.include_router(get_router)
router.include_router(patch_router)
