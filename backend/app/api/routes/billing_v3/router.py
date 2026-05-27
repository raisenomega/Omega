"""Main router de billing_v3 · agrupa checkout + webhook + upgrade-aria + video-pack bajo /billing prefix."""
from fastapi import APIRouter
from app.api.routes.billing_v3.handlers.create_checkout import router as checkout_router
from app.api.routes.billing_v3.handlers.stripe_webhook import router as webhook_router
from app.api.routes.billing_v3.handlers.upgrade_aria import router as upgrade_aria_router
from app.api.routes.billing_v3.handlers.checkout_video_pack import router as video_pack_router
from app.api.routes.billing_v3.handlers.checkout_credit_pack import router as credit_pack_router
from app.api.routes.billing_v3.handlers.admin_credits import router as admin_credits_router
from app.api.routes.billing_v3.handlers.schedule_downgrade import router as schedule_downgrade_router

router = APIRouter(prefix="/billing", tags=["Billing V3"])
router.include_router(checkout_router)
router.include_router(webhook_router)
router.include_router(upgrade_aria_router)
router.include_router(video_pack_router)
router.include_router(credit_pack_router)
router.include_router(admin_credits_router)
router.include_router(schedule_downgrade_router)
