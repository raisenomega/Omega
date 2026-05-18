"""
OMEGA · GET /api/v1/admin/solicitudes/
Lista todas las solicitudes de upsell para el superadmin
R-LINES-001: < 200L · Solo role=owner
"""
from fastapi import HTTPException, status, Header
from typing import Optional

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

from ..upsell.upsell_models import AdminSolicitudesResponse, AdminSolicitudDetailResponse, SolicitudResponse


async def get_solicitudes(
    authorization: Optional[str] = Header(None),
    filter_status: str | None = None,
) -> AdminSolicitudesResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo superadmin")

    query = supabase.client.table("upsell_solicitudes").select("*").order("created_at", desc=True)

    if filter_status:
        query = query.eq("status", filter_status)

    result = query.execute()
    rows = result.data or []

    solicitudes = [SolicitudResponse(**r) for r in rows]
    pending = [s for s in solicitudes if s.status == "pending"]
    accepted = [s for s in solicitudes if s.status == "accepted"]
    monthly_revenue = sum(s.monthly_price for s in accepted)

    return AdminSolicitudesResponse(
        success=True,
        data=solicitudes,
        total=len(solicitudes),
        pending_count=len(pending),
        monthly_revenue_upsell=monthly_revenue,
    )


async def get_solicitud_detail(
    solicitud_id: str,
    authorization: Optional[str] = Header(None),
) -> AdminSolicitudDetailResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo superadmin")

    result = supabase.client.table("upsell_solicitudes").select("*").eq("id", solicitud_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    return AdminSolicitudDetailResponse(success=True, data=SolicitudResponse(**result.data))
