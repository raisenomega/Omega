"""Main router clients_v3 · agrupa profile + onboarding bajo /clients prefix."""
from fastapi import APIRouter
from app.api.routes.clients_v3.handlers.get_client_profile import router as get_router
from app.api.routes.clients_v3.handlers.update_client_profile import router as patch_router
from app.api.routes.clients_v3.handlers.create_client_onboarding import router as onboarding_router
from app.api.routes.clients_v3.handlers.upload_brand_file import router as upload_router
from app.api.routes.clients_v3.handlers.parse_brand_pdf import router as pdf_router

router = APIRouter(prefix="/clients", tags=["Clients V3"])
router.include_router(get_router)
router.include_router(patch_router)
router.include_router(onboarding_router)
router.include_router(upload_router)
router.include_router(pdf_router)
