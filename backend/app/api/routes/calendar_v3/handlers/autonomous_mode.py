"""PATCH /calendar-v3/autonomous-mode · enciende/apaga el Modo Autónomo (REX) por negocio.

Aislamiento: resolve_client_or_403 (owner/reseller del client_id · NUNCA client_id crudo
del body sin verificar). Setea clients.autonomous_mode_on = CONSENTIMIENTO humano (distinto
de rex_addon_active = compra). Solo se puede ENCENDER si el add-on está comprado; apagar OK.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3._access import resolve_client_or_403
from app.bc_cognition.infrastructure import owner_accounts_repository as owners
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


class AutonomousModeRequest(BaseModel):
    client_id: str
    enabled: bool


@router.get("/autonomous-mode/{client_id}")
async def get_autonomous_mode(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> dict[str, bool]:
    """Flags del negocio para renderizar el toggle (gating + estado actual).

    rex_addon_active EFECTIVO (mismo helper que el worker): columna OR cuenta-dueño exenta
    (owner_accounts) → la exención llega a la UI (toggle se MUESTRA en negocios de cuenta-dueño).
    Mostrar ≠ encender: autonomous_mode_on (consentimiento) NO se toca acá.
    """
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id)  # 404/403 si no es dueño
    return {
        "rex_addon_active": owners.is_rex_addon_effective(
            client.get("rex_addon_active"), client.get("user_id")),
        "autonomous_mode_on": bool(client.get("autonomous_mode_on")),
    }


@router.patch("/autonomous-mode")
async def set_autonomous_mode(
    request: AutonomousModeRequest,
    authorization: Optional[str] = Header(None),
) -> dict[str, bool]:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # 404/403 si no es dueño
    if request.enabled and not client.get("rex_addon_active"):
        raise HTTPException(status_code=403, detail="rex_addon_not_active")
    sb = get_supabase_service()
    sb.client.table("clients").update(
        {"autonomous_mode_on": request.enabled}
    ).eq("id", request.client_id).execute()
    return {"autonomous_mode_on": request.enabled}
