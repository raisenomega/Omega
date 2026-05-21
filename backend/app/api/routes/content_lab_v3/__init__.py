"""content_lab_v3 · V3 endpoints generación de contenido (P0 corazón sistema).

POST /api/v1/content-lab/generate · text generation via anthropic_adapter
   (I1 único entry · I2 routing content_creator → Sonnet 4.6).
"""
from app.api.routes.content_lab_v3.router import router

__all__ = ["router"]
