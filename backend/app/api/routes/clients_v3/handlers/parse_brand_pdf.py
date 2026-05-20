"""POST /api/v1/clients/{client_id}/parse-brand-pdf · STUB DEBT-039.

Fase 3: extrae brand info de PDF con pypdf + Claude Haiku auto-populate
client_context. Hoy retorna 501 con detail explicativo.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.post("/{client_id}/parse-brand-pdf")
async def parse_brand_pdf(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    await get_current_user(authorization)
    raise HTTPException(
        status_code=501,
        detail="DEBT-039 · pypdf + Haiku extraction pendiente Fase 3",
    )
