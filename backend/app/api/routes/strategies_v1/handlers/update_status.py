"""PATCH /api/v1/strategies/{id}/status · archivar / marcar usada (DEBT-096 Fase 1).
Ownership scopeado en el UPDATE (client_ids) → 404 si no es del usuario (sin fuga)."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.bc_cognition.infrastructure import strategy_repository as strat
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
_VALID = {"active", "used", "archived"}


class StatusBody(BaseModel):
    estado: str


@router.patch("/{strategy_id}/status")
async def update_status(strategy_id: str, body: StatusBody,
                        authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    if body.estado not in _VALID:
        raise HTTPException(status_code=422, detail="estado_invalido")
    client_ids = reader.get_accessible_client_ids(user["id"])
    n = strat.update_strategy_status(get_supabase_service(), strategy_id, body.estado, client_ids)
    if n == 0:
        raise HTTPException(status_code=404, detail="strategy_not_found")
    return {"id": strategy_id, "estado": body.estado}
