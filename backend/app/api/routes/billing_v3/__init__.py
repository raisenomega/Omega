"""billing_v3 · routes V3 sobre bc_billing/ bounded context.

Sustituye al `billing/` legacy (DEBT-036). Path canónico
`/api/v1/billing/*` apunta a este módulo desde main.py.
"""
from app.api.routes.billing_v3.router import router

__all__ = ["router"]
