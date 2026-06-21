"""Main router intelligence · /intelligence prefix · Centro de Inteligencia Fase 1."""
from fastapi import APIRouter

from app.api.routes.intelligence.handlers.aeo_check import router as aeo_check_router
from app.api.routes.intelligence.handlers.analytics_social import router as analytics_social_router
from app.api.routes.intelligence.handlers.chips import router as chips_router
from app.api.routes.intelligence.handlers.geo_check import router as geo_check_router
from app.api.routes.intelligence.handlers.web_analysis import router as web_analysis_router

router = APIRouter(prefix="/intelligence", tags=["Intelligence 🧠"])
router.include_router(web_analysis_router)
router.include_router(geo_check_router)
router.include_router(aeo_check_router)
router.include_router(chips_router)  # Fase 2 · /intelligence/chips/{meta,google}
router.include_router(analytics_social_router)  # Analytics · /intelligence/analytics (Zernio · DEBT-034)
