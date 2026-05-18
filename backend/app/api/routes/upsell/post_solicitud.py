"""
OMEGA · POST /api/v1/upsell/solicitud/
Crea una solicitud de upsell que llega al superadmin
R-LINES-001: < 200L
"""
import time
from datetime import datetime, timezone
from fastapi import HTTPException, status, Header
from typing import Optional

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

from .upsell_models import SolicitudCreate, SolicitudCreateResponse, SolicitudResponse

VALID_ITEM_CODES = {
    # Departamentos
    "atlas_marketing", "luna_tech", "rex_operations", "vera_finance",
    "kira_community", "oracle_futures", "sophia_people", "sentinel_security",
    # Agentes individuales
    "ATLAS","RAFA","MAYA","DUDA","LOLA","LUAN","DANI","SARA","MALU",
    "LUNA","ARCH","PIXEL","PULSE-TECH","SCRIBE","SHIELD",
    "REX","ANCHOR","ECHO","MIRROR-OPS","ONYX","RESELL-OPS",
    "VERA","GUARD","LEDGER-FIN","REPORT","SCOPE",
    "KIRA","CONSTRUCT","ESTATE","HAVEN","NURTURE","REVIEW",
    "ORACLE","MIRROR-FUT","NEXUS","SCOUT","VEGA",
    "SOPHIA","LEDGER-HR","PROMETHEUS","PULSE","RECRUIT","TRAINER",
    "SENTINEL","ARCH-SCAN","AUTO-HEALER","COMPLIANCE","DB-GUARDIAN",
    "DEBT-HUNTER","DEP-WATCH","FORTRESS","MIGRATION-VAL","PULSE-MON",
    "SENT-BRAIN","SPEED-ANZ","VAULT",
    # Nova (precio especial sin descuento)
    "NOVA",
}


def _generate_id() -> str:
    return f"{int(time.time() * 1000)}"


async def post_solicitud(
    payload: SolicitudCreate,
    authorization: Optional[str] = Header(None),
) -> SolicitudCreateResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    # Validar que el client_id coincide con el usuario autenticado
    # (owner puede crear para cualquier cliente)
    if user.get("role") not in ("client", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    if payload.item_code not in VALID_ITEM_CODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Código de agente inválido: {payload.item_code}",
        )

    if payload.monthly_price <= 0 or payload.new_monthly_total <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Precio inválido",
        )

    client_row = supabase.client.table("clients").select("id, name, email, plan").eq("id", payload.client_id).single().execute()
    if not client_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    client = client_row.data

    # Verificar que no existe solicitud pendiente para el mismo agente
    existing = (
        supabase.client.table("upsell_solicitudes")
        .select("id")
        .eq("client_id", payload.client_id)
        .eq("item_code", payload.item_code)
        .eq("status", "pending")
        .execute()
    )
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una solicitud pendiente para este agente",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    solicitud_id = _generate_id()

    record = {
        "id": solicitud_id,
        "client_id": payload.client_id,
        "client_name": client["name"],
        "client_email": client["email"],
        "current_plan": payload.current_plan,
        "request_type": payload.request_type,
        "item_name": payload.item_name,
        "item_code": payload.item_code,
        "monthly_price": payload.monthly_price,
        "new_monthly_total": payload.new_monthly_total,
        "client_message": payload.client_message,
        "status": "pending",
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    result = supabase.client.table("upsell_solicitudes").insert(record).execute()
    if not result.data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear solicitud")

    row = result.data[0]
    return SolicitudCreateResponse(
        success=True,
        data=SolicitudResponse(**row),
        message="Solicitud enviada. El equipo de OMEGA la procesará en breve.",
    )
