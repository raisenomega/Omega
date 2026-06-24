"""Router OAuth (RONDA D · /oauth) · Google. 503 honesto sin credenciales."""
from fastapi import APIRouter
from app.api.routes.oauth.handlers.google_oauth import router as google_router

router = APIRouter(prefix="/oauth", tags=["OAuth"])
router.include_router(google_router)
