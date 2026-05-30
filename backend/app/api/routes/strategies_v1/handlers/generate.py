"""POST /api/v1/strategies/generate · genera una estrategia on-demand (DEBT-096 Fase 1).
A1+A9: handler → use case (NO toca infrastructure directo)."""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.bc_cognition.application.use_generate_strategy import use_generate_strategy

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate")
async def generate_strategy(authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    result, err = await use_generate_strategy(user["id"])
    if err or not result:
        status = 403 if err and err.code == "forbidden" else 503
        msg = err.message if err else "No se pudo generar la estrategia"
        logger.warning(f"strategy generate failed · {status} · {msg}")
        raise HTTPException(status_code=status, detail=msg)
    return {"id": result.id, "titulo": result.titulo, "contenido": result.contenido}
