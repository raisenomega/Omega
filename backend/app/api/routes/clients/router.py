"""
Clients Router
Registers all client sub-routers under /clients prefix
"""
from fastapi import APIRouter
import logging
from app.api.routes.clients import list, create, read, update, delete

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])

# CRUD operations
router.include_router(list.router)
router.include_router(create.router)
router.include_router(read.router)
router.include_router(update.router)
router.include_router(delete.router)

logger.info("Client routers registered successfully")
