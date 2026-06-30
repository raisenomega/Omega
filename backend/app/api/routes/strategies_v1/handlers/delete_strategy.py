"""DELETE /api/v1/strategies/{id} · ⚠️ BORRADO PERMANENTE (hard delete · irreversible · Fase 2).
Ownership scopeado en el DELETE (client_ids del servidor) → 404 si no es del usuario (sin fuga ·
patron update_status/use). La fila desaparece de verdad: ningun FK la referencia como padre."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.bc_cognition.infrastructure import strategy_repository as strat
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str,
                          authorization: Optional[str] = Header(None)) -> dict[str, object]:
    user = await get_current_user(authorization)
    client_ids = reader.get_accessible_client_ids(user["id"])
    n = strat.delete_strategy(get_supabase_service(), strategy_id, client_ids)
    if n == 0:
        raise HTTPException(status_code=404, detail="strategy_not_found")
    return {"deleted": True, "id": strategy_id}
