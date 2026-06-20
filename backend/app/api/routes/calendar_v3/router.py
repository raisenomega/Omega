"""Main router calendar_v3.

Sub-routers con prefix diferenciado:
- list + status bajo /calendar (back-compat con UI existente)
- schedule_post bajo /calendar-v3 (DEBT-CL-017 + path X · path distintivo
  para evitar colisión con /calendar/schedule/ del legacy)
"""
from fastapi import APIRouter
from app.api.routes.calendar_v3.handlers.list_calendar import router as list_router
from app.api.routes.calendar_v3.handlers.update_status import router as status_router
from app.api.routes.calendar_v3.handlers.schedule_post import router as schedule_router
from app.api.routes.calendar_v3.handlers.autonomous_mode import router as autonomous_router

router = APIRouter()
router.include_router(list_router, prefix="/calendar", tags=["Calendar V3 Read"])
router.include_router(status_router, prefix="/calendar", tags=["Calendar V3 Status"])
router.include_router(schedule_router, prefix="/calendar-v3", tags=["Calendar V3 Schedule"])
router.include_router(autonomous_router, prefix="/calendar-v3", tags=["Calendar V3 Autonomous"])
