"""Main router calendar_v3 · GET list + PATCH status bajo /calendar prefix."""
from fastapi import APIRouter
from app.api.routes.calendar_v3.handlers.list_calendar import router as list_router
from app.api.routes.calendar_v3.handlers.update_status import router as status_router

router = APIRouter(prefix="/calendar", tags=["Calendar V3"])
router.include_router(list_router)
router.include_router(status_router)
