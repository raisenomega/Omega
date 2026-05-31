"""POST /api/v1/strategies/generate · genera una estrategia on-demand (DEBT-096 Fase 1).
A1+A9: handler orquesta · resuelve rol + gatea budget ($ · check_budget → 402, calcado de
generate_text.py:52) ANTES de la generación cara · luego delega al use case."""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_billing.application.credits_service import check_budget
from app.bc_cognition.application._aria_role import resolve_role
from app.bc_cognition.application.use_generate_strategy import use_generate_strategy
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


class GenerateStrategyRequest(BaseModel):
    # Switcher V1: negocio activo del switcher. Ausente → legacy (cliente propio vía resolve_role).
    client_id: Optional[str] = None


@router.post("/generate")
async def generate_strategy(request: GenerateStrategyRequest = GenerateStrategyRequest(),
                            authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    if request.client_id:
        client = resolve_client_or_403(user["id"], request.client_id)  # verifica acceso (404/403)
        client_id, reseller_id = str(client["id"]), None
    else:
        _role, client_id, reseller_id, _level = resolve_role(get_supabase_service(), user["id"])
        if not client_id:
            raise HTTPException(status_code=403, detail="Las estrategias se generan para un negocio (cliente).")
    if not await check_budget(client_id):  # DEBT-052: budget prepagado agotado → 402 (no genera ni gasta)
        raise HTTPException(status_code=402, detail="credits_exhausted")
    result, err = await use_generate_strategy(client_id, reseller_id)
    if err or not result:
        msg = err.message if err else "No se pudo generar la estrategia"
        logger.warning(f"strategy generate failed · {msg}")
        raise HTTPException(status_code=503, detail=msg)
    return {"id": result.id, "titulo": result.titulo, "contenido": result.contenido}
