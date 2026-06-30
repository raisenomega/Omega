"""Router strategies_v1 · DEBT-096 Fase 1 · agrupa generate + list + update bajo /strategies
(plural · NO colisiona con el router legacy /strategy singular)."""
from fastapi import APIRouter
from app.api.routes.strategies_v1.handlers.generate import router as generate_router
from app.api.routes.strategies_v1.handlers.list_strategies import router as list_router
from app.api.routes.strategies_v1.handlers.update_status import router as update_router
from app.api.routes.strategies_v1.handlers.record_use import router as use_router
from app.api.routes.strategies_v1.handlers.delete_strategy import router as delete_router
from app.api.routes.strategies_v1.handlers.idea_usages import router as idea_usages_router

router = APIRouter(prefix="/strategies", tags=["Strategies V1"])
router.include_router(generate_router)
router.include_router(list_router)
router.include_router(update_router)
router.include_router(use_router)
router.include_router(idea_usages_router)  # ANTES de delete · ruta literal used-ideas/... gana al {strategy_id}
router.include_router(delete_router)
