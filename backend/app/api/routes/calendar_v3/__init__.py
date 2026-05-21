"""calendar_v3 · V3 endpoints scheduled_posts (DEBT-033 CERRADA).

GET   /api/v1/calendar/         · lista scheduled_posts del mes con JOIN.
PATCH /api/v1/calendar/{id}/status · pending<->cancelled transitions.
"""
from app.api.routes.calendar_v3.router import router

__all__ = ["router"]
