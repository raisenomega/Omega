"""Router OAuth (RONDA D · /oauth) · Google. 503 honesto sin credenciales."""
from fastapi import APIRouter
from app.api.routes.oauth.handlers.google_oauth import router as google_router
from app.api.routes.oauth.handlers.google_ga4 import router as google_ga4_router

router = APIRouter(prefix="/oauth", tags=["OAuth"])
router.include_router(google_router)
router.include_router(google_ga4_router)
