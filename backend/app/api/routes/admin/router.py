"""
OMEGA · Admin Router
GET  /api/v1/admin/solicitudes/
GET  /api/v1/admin/solicitudes/{id}/
PATCH /api/v1/admin/solicitudes/{id}/accept/
PATCH /api/v1/admin/solicitudes/{id}/decline/
R-LINES-001: < 200L · Solo role=owner
"""
from typing import Optional
from fastapi import APIRouter, Header, Query
from .get_solicitudes import get_solicitudes, get_solicitud_detail
from .patch_solicitud import patch_solicitud_accept, patch_solicitud_decline
from ..upsell.upsell_models import (
    AdminSolicitudesResponse,
    AdminSolicitudDetailResponse,
    SolicitudActionResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/solicitudes/", response_model=AdminSolicitudesResponse)
async def list_solicitudes(
    status: Optional[str] = Query(None, description="Filtrar por estado: pending | accepted | declined"),
    authorization: Optional[str] = Header(None),
) -> AdminSolicitudesResponse:
    """
    Lista todas las solicitudes de upsell.
    Incluye conteo de pendientes y revenue adicional del mes.
    Solo accesible para role=owner (superadmin).
    """
    return await get_solicitudes(authorization, filter_status=status)


@router.get("/solicitudes/{solicitud_id}/", response_model=AdminSolicitudDetailResponse)
async def solicitud_detail(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> AdminSolicitudDetailResponse:
    """Detalle de una solicitud individual."""
    return await get_solicitud_detail(solicitud_id, authorization)


@router.patch("/solicitudes/{solicitud_id}/accept/", response_model=SolicitudActionResponse)
async def accept_solicitud(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> SolicitudActionResponse:
    """
    Acepta la solicitud → cobra por Stripe usando el método ya registrado del cliente
    → activa el agente → notifica al cliente.
    Solo accesible para role=owner.
    """
    return await patch_solicitud_accept(solicitud_id, authorization)


@router.patch("/solicitudes/{solicitud_id}/decline/", response_model=SolicitudActionResponse)
async def decline_solicitud(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> SolicitudActionResponse:
    """Declina la solicitud. Solo accesible para role=owner."""
    return await patch_solicitud_decline(solicitud_id, authorization)
