"""
Clients Router
Registers all client sub-routers under /clients prefix
"""
from fastapi import APIRouter
import logging
from app.api.routes.clients import list, create, read, update, delete
from app.api.routes.clients import detail, agents, content, billing, activity, home

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])

# CRUD operations
router.include_router(list.router)
router.include_router(create.router)
router.include_router(read.router)
router.include_router(update.router)
router.include_router(delete.router)

# Client detail endpoints
router.include_router(detail.router)
router.include_router(home.router)
router.include_router(agents.router)
router.include_router(content.router)
router.include_router(billing.router)
router.include_router(activity.router)

logger.info("Client routers registered successfully")
