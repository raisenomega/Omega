"""
Auth Main Router
Registers all auth sub-routers under /auth prefix
"""
from fastapi import APIRouter
import logging

# Import sub-routers
from app.api.routes.auth import (
    register,
    login,
    profile,
    avatar,
)

# Create main router
router = APIRouter(prefix="/auth", tags=["auth"])

# Configure logging
logger = logging.getLogger(__name__)

# Register sub-routers
router.include_router(register.router, tags=["auth-register"])
router.include_router(login.router, tags=["auth-login"])
router.include_router(profile.router, tags=["auth-profile"])
router.include_router(avatar.router, tags=["auth-avatar"])

logger.info("Auth routers registered successfully")
