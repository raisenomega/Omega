"""Main router intelligence · /intelligence prefix · Centro de Inteligencia Fase 1."""
from fastapi import APIRouter

from app.api.routes.intelligence.handlers.web_analysis import router as web_analysis_router

router = APIRouter(prefix="/intelligence", tags=["Intelligence 🧠"])
router.include_router(web_analysis_router)
