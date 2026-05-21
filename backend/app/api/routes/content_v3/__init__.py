"""content_v3 · V3 endpoints content_lab_generated (DEBT-033 parcial).

GET   /api/v1/content/         · lista content_lab_generated del usuario
PATCH /api/v1/content/{id}/save · toggle is_saved + agent_memory aprendizaje
"""
from app.api.routes.content_v3.router import router

__all__ = ["router"]
