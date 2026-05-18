"""
OMEGA · Upsell Router
POST /api/v1/upsell/solicitud/
R-LINES-001: < 200L
"""
from fastapi import APIRouter, Header
from typing import Optional
from .post_solicitud import post_solicitud
from .upsell_models import SolicitudCreate, SolicitudCreateResponse

router = APIRouter(prefix="/upsell", tags=["upsell"])


@router.post("/solicitud/", response_model=SolicitudCreateResponse)
async def create_solicitud(
    payload: SolicitudCreate,
    authorization: Optional[str] = Header(None),
) -> SolicitudCreateResponse:
    """
    Crea una solicitud de upsell (agente individual o departamento completo).
    La solicitud llega al superadmin en su panel de Solicitudes.
    El cliente solo necesita llenar client_message (opcional).
    Todos los demás campos vienen del frontend automáticamente.
    """
    return await post_solicitud(payload, authorization)
