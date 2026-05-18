"""
Reseller Main Router
Registers all reseller sub-routers under /resellers prefix
"""
from fastapi import APIRouter
import logging

# Import sub-routers
from app.api.routes.resellers import (
    admin,
    dashboard,
    clients,
    public,
    leads,
    branding,
    detail,
    reseller_clients,
    reseller_billing,
    stats,
    reseller_activity
)

# Create main router
router = APIRouter(prefix="/resellers", tags=["resellers"])

# Configure logging
logger = logging.getLogger(__name__)

# Register sub-routers
# Admin routes (owner only)
router.include_router(admin.router, tags=["resellers-admin"])

# Dashboard routes
router.include_router(dashboard.router, tags=["resellers-dashboard"])

# Client management routes
router.include_router(clients.router, tags=["resellers-clients"])

# Public routes (no auth)
router.include_router(public.router, tags=["resellers-public"])

# Lead management routes
router.include_router(leads.router, tags=["resellers-leads"])

# Branding routes
router.include_router(branding.router, tags=["resellers-branding"])

# Reseller detail routes
router.include_router(detail.router, tags=["resellers-detail"])
router.include_router(reseller_clients.router, tags=["resellers-detail"])
router.include_router(reseller_billing.router, tags=["resellers-detail"])
router.include_router(stats.router, tags=["resellers-detail"])
router.include_router(reseller_activity.router, tags=["resellers-detail"])

logger.info("Reseller routers registered successfully")
