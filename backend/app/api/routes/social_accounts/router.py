"""
Social Accounts Router
Aggregates all social account endpoints
"""
from fastapi import APIRouter
from app.api.routes.social_accounts import list, create, read, update, delete, with_context

router = APIRouter(prefix="/social-accounts", tags=["social-accounts"])

# Register all sub-routers
router.include_router(list.router)
router.include_router(create.router)
router.include_router(read.router)
router.include_router(update.router)
router.include_router(delete.router)
router.include_router(with_context.router, prefix="/with-context", tags=["social-accounts-context"])
