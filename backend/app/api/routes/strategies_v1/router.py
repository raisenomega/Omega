"""Router strategies_v1 · DEBT-096 Fase 1 · agrupa generate + list + update bajo /strategies
(plural · NO colisiona con el router legacy /strategy singular)."""
from fastapi import APIRouter
from app.api.routes.strategies_v1.handlers.generate import router as generate_router
from app.api.routes.strategies_v1.handlers.list_strategies import router as list_router
from app.api.routes.strategies_v1.handlers.update_status import router as update_router
from app.api.routes.strategies_v1.handlers.record_use import router as use_router

router = APIRouter(prefix="/strategies", tags=["Strategies V1"])
router.include_router(generate_router)
router.include_router(list_router)
router.include_router(update_router)
router.include_router(use_router)
