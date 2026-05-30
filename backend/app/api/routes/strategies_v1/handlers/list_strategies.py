"""GET /api/v1/strategies/?estado=active|archived · estrategias del usuario (DEBT-096 Fase 1).
Ownership vía get_accessible_client_ids (RLS-equivalente · cliente y reseller)."""
from typing import Optional
from fastapi import APIRouter, Header, Query
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.bc_cognition.infrastructure import strategy_repository as strat
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
_VALID = {"active", "archived", "used"}


@router.get("/")
async def list_strategies(estado: str = Query("active"),
                          authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    if estado not in _VALID:
        estado = "active"
    client_ids = reader.get_accessible_client_ids(user["id"])
    rows = strat.list_strategies(get_supabase_service(), client_ids, estado)
    return {"items": rows}
