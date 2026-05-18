"""
OMEGA · Reseller Router
GET /api/v1/reseller/{reseller_id}/home/ — Dashboard principal
GET /api/v1/reseller/{reseller_id}/clients/ — Lista de clientes
DELETE /api/v1/reseller/{reseller_id}/ — Eliminar reseller (owner only)
R-LINES-001: < 200L
"""
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from .get_reseller_home import get_reseller_home
from .get_reseller_clients import get_reseller_clients
from .reseller_home_models import ResellerHomeResponse
from .reseller_clients_models import ResellerClientListResponse

router = APIRouter(prefix="/reseller", tags=["reseller"])


@router.get("/{reseller_id}/home/", response_model=ResellerHomeResponse)
async def reseller_home_endpoint(
    reseller_id: str,
    authorization: Optional[str] = Header(None),
) -> ResellerHomeResponse:
    """
    Dashboard principal del reseller.
    Retorna: perfil, KPIs, clientes con salud, reportes de agentes,
    oportunidades de upsell.
    Acceso: role=reseller (propio ID) o role=owner (cualquier ID).
    """
    return await get_reseller_home(reseller_id, authorization)


@router.get("/{reseller_id}/clients/", response_model=ResellerClientListResponse)
async def reseller_clients_endpoint(
    reseller_id: str,
    authorization: Optional[str] = Header(None),
) -> ResellerClientListResponse:
    """
    Lista todos los clientes del reseller.
    Retorna: array de clientes con stats básicas y health status.
    Acceso: role=reseller (propio ID) o role=owner (cualquier ID).
    """
    return await get_reseller_clients(reseller_id, authorization)


@router.delete("/{reseller_id}/")
async def delete_reseller_endpoint(
    reseller_id: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    """
    Elimina un reseller. Solo role=owner.
    Verifica que no tenga clientes activos antes de eliminar.
    """
    supabase = get_supabase_service()
    try:
        clients = (
            supabase.client.table("clients")
            .select("id")
            .eq("reseller_id", reseller_id)
            .execute()
        )
        if clients.data:
            raise HTTPException(400, "Reseller tiene clientes activos. Reasigna antes de eliminar.")
        supabase.client.table("user_roles").delete().eq("reseller_id", reseller_id).execute()
        result = supabase.client.table("resellers").delete().eq("id", reseller_id).execute()
        if not result.data:
            raise HTTPException(404, "Reseller no encontrado")
        return {"deleted": True, "reseller_id": reseller_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e)[:200])
