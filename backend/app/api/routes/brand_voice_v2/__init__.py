"""brand_voice_v2 · V3 read-only endpoints · /api/v1/brand-voice/* (Sprint 2 ②.A).

GET /summary · expone corpus_count + latest_approvals + top_keywords
para la página /brand-voice del cliente. Cero writes · sin edits.
"""
from app.api.routes.brand_voice_v2.router import router

__all__ = ["router"]
