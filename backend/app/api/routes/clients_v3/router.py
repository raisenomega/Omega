"""Main router clients_v3 · agrupa profile + onboarding bajo /clients prefix."""
from fastapi import APIRouter
from app.api.routes.clients_v3.handlers.get_client_profile import router as get_router
from app.api.routes.clients_v3.handlers.update_client_profile import router as patch_router
from app.api.routes.clients_v3.handlers.create_client_onboarding import router as onboarding_router
from app.api.routes.clients_v3.handlers.upload_brand_file import router as upload_router
from app.api.routes.clients_v3.handlers.parse_brand_pdf import router as pdf_router
from app.api.routes.clients_v3.handlers.get_onboarding_data import router as get_data_router
from app.api.routes.clients_v3.handlers.update_onboarding_data import router as patch_data_router
from app.api.routes.clients_v3.handlers.list_client_social_accounts import router as social_accounts_router
from app.api.routes.clients_v3.handlers.upload_client_context import router as upload_context_router
from app.api.routes.clients_v3.handlers.zernio_mapping import router as zernio_mapping_router

router = APIRouter(prefix="/clients", tags=["Clients V3"])
router.include_router(get_router)
router.include_router(patch_router)
router.include_router(onboarding_router)
router.include_router(upload_router)
router.include_router(pdf_router)
router.include_router(get_data_router)
router.include_router(patch_data_router)
router.include_router(social_accounts_router)
router.include_router(upload_context_router)
router.include_router(zernio_mapping_router)
