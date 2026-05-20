"""Main router de billing_v3 · agrupa checkout + webhook bajo /billing prefix."""
from fastapi import APIRouter
from app.api.routes.billing_v3.handlers.create_checkout import router as checkout_router
from app.api.routes.billing_v3.handlers.stripe_webhook import router as webhook_router

router = APIRouter(prefix="/billing", tags=["Billing V3"])
router.include_router(checkout_router)
router.include_router(webhook_router)
