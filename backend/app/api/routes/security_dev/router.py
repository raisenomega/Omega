"""Security Dev router · prefijo /security-dev · solo is_super_owner."""
from typing import Optional
from fastapi import APIRouter, Header
from app.api.routes.security_dev.handlers.health_check import handle_dev_health
from app.api.routes.security_dev.handlers.sentinel_data import handle_sentinel_data
from app.api.routes.security_dev.handlers.guardian_data import handle_guardian_data
from app.api.routes.security_dev.handlers.hermes_data import handle_hermes_data

router = APIRouter(prefix="/security-dev", tags=["Security Dev 🔐"])


@router.get("/health")
async def dev_health(authorization: Optional[str] = Header(None)):
    return await handle_dev_health(authorization)


@router.get("/sentinel")
async def sentinel_data(authorization: Optional[str] = Header(None)):
    return await handle_sentinel_data(authorization)


@router.get("/guardian")
async def guardian_data(authorization: Optional[str] = Header(None)):
    return await handle_guardian_data(authorization)


@router.get("/hermes")
async def hermes_data(authorization: Optional[str] = Header(None)):
    return await handle_hermes_data(authorization)
