"""
Billing Main Router
Registers all billing sub-routers under /billing prefix
"""
from fastapi import APIRouter
import logging

# Import sub-routers
from app.api.routes.billing import (
    checkout,
    webhook,
    subscription,
)

# Create main router
router = APIRouter(prefix="/billing", tags=["billing"])

# Configure logging
logger = logging.getLogger(__name__)

# Register sub-routers
router.include_router(checkout.router, tags=["billing-checkout"])
router.include_router(webhook.router, tags=["billing-webhook"])
router.include_router(subscription.router, tags=["billing-subscription"])

logger.info("Billing routers registered successfully")
