"""REDISEÑO Estrategias Fase A · "la idea es la unidad":
- POST /api/v1/strategies/{id}/use-idea · registra el uso de UNA idea (1 fila en strategy_idea_usages).
  Flip a estado='used' SOLO cuando se usaron TODAS las ideas (count == len(posts_sugeridos)).
- GET  /api/v1/strategies/used-ideas   · lista las ideas usadas del cliente (Fase B · vista Usadas).
Ownership: client_ids del servidor en el WHERE → 404 sin fuga (patron update_status/use/delete)."""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_v3 import _content_reader as reader
from app.bc_cognition.infrastructure import strategy_repository as strat
from app.bc_cognition.infrastructure import strategy_idea_usage_repository as usages
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


class UseIdeaBody(BaseModel):
    idea_idx: int = Field(..., ge=0)                          # índice de la idea en posts_sugeridos
    platform: str = Field(..., min_length=1, max_length=64)  # red normalizada
    brief: str = Field(..., min_length=1)                     # texto de la idea usada


@router.post("/{strategy_id}/use-idea")
async def use_idea(strategy_id: str, body: UseIdeaBody,
                   authorization: Optional[str] = Header(None)) -> dict[str, object]:
    user = await get_current_user(authorization)
    client_ids = reader.get_accessible_client_ids(user["id"])
    sb = get_supabase_service()
    owned = strat.get_strategy_owned(sb, strategy_id, client_ids)
    if not owned:
        raise HTTPException(status_code=404, detail="strategy_not_found")
    usages.record_idea_use(sb, strategy_id, owned["client_id"], body.idea_idx, body.platform, body.brief)
    total = len((owned.get("contenido") or {}).get("posts_sugeridos") or [])
    used = usages.count_idea_usages(sb, strategy_id)
    all_used = total > 0 and used >= total
    if all_used:  # flip SOLO cuando se usaron todas las ideas (corazon del modelo nuevo)
        strat.update_strategy_status(sb, strategy_id, "used", client_ids)
    return {"id": strategy_id, "idea_idx": body.idea_idx, "used_count": used, "total": total, "all_used": all_used}


@router.get("/used-ideas")
async def used_ideas(authorization: Optional[str] = Header(None)) -> dict[str, object]:
    user = await get_current_user(authorization)
    client_ids = reader.get_accessible_client_ids(user["id"])
    return {"items": usages.list_idea_usages(get_supabase_service(), client_ids)}
