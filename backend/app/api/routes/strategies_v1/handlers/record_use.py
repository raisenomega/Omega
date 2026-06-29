"""POST /api/v1/strategies/{id}/use · registra el uso de una estrategia (ARCO MEDICION CAPA 1).
Escribe strategies.last_used = {platform, brief, at}. mark_used=True → ademas estado='used' (boton
'Usar' completo · va a Usadas); mark_used=False → solo last_used, estado intacto (la flecha · opcion ii).
Ownership scopeado en el UPDATE (client_ids) → 404 si no es del usuario (sin fuga · patron update_status)."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.bc_cognition.infrastructure import strategy_repository as strat
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


class UseBody(BaseModel):
    platform: str = Field(..., min_length=1, max_length=64)  # red normalizada o "completa"
    brief: str = Field(..., min_length=1)                     # texto enviado a Content Lab (sin limite raro)
    mark_used: bool = False                                   # True = "Usar" completo · False = flecha


@router.post("/{strategy_id}/use")
async def record_use(strategy_id: str, body: UseBody,
                     authorization: Optional[str] = Header(None)) -> dict[str, object]:
    user = await get_current_user(authorization)
    last_used: dict[str, str] = {
        "platform": body.platform,
        "brief": body.brief,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    client_ids = reader.get_accessible_client_ids(user["id"])
    n = strat.record_use(get_supabase_service(), strategy_id, last_used, body.mark_used, client_ids)
    if n == 0:
        raise HTTPException(status_code=404, detail="strategy_not_found")
    return {"id": strategy_id, "last_used": last_used}
