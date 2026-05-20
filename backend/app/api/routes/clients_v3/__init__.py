"""clients_v3 · V3 endpoints client profile (DEBT-033 parcial).

GET  /api/v1/clients/profile  · perfil del cliente del usuario auth
PATCH /api/v1/clients/profile · update name/industry/region

Validación industry/region contra app/domain/client_constants.py (A2).
"""
from app.api.routes.clients_v3.router import router

__all__ = ["router"]
