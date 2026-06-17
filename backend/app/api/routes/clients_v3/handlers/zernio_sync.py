"""B-2 · zernio-sync · captura el accountId que el cliente conectó, CON HARDENING anti-cross-publish.

Tras el OAuth (botón 'Ya conecté · verificar'), OMEGA lee SOLO el profile del negocio
(list_accounts(profileId)) y guarda el binding en social_accounts. Defensa (cierra el círculo
del incidente 8-jun en el momento de conectar, no solo al elegir):
  · handle AUTORITATIVO de Zernio (username/displayName) · jamás de un body del frontend.
  · re-valida que el account pertenece al profileId de ESTE negocio (no confía solo en el filtro).
  · si la cuenta no cayó en el profile correcto → 422 honesto, NO guarda (regla cero-mocks).
SEGURIDAD: service_role BYPASSA RLS → user_owns_client ANTES de tocar nada.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.bc_cognition.infrastructure.zernio_adapter import list_accounts
from app.infrastructure.supabase_service import get_supabase_service

router = APIRouter()


def _profile_of(account: dict) -> Optional[str]:
    """profileId del account · Zernio lo devuelve como objeto {_id, name} (o id plano)."""
    p = account.get("profileId")
    if isinstance(p, dict):
        return str(p.get("_id")) if p.get("_id") else None
    return str(p) if p else None


@router.post("/{client_id}/social-accounts/{platform}/zernio-sync")
async def zernio_sync(client_id: str, platform: str,
                      authorization: Optional[str] = Header(None)) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):          # OWNERSHIP GUARD
        raise HTTPException(status_code=403, detail="client_access_denied")
    pid = client.get("zernio_profile_id")
    if not pid:
        raise HTTPException(status_code=409, detail="zernio_profile_missing")
    pid = str(pid)
    # HARDENING: cuentas SOLO del profile del negocio + RE-VALIDAR pertenencia (no confiar solo en el filtro).
    accounts = await list_accounts(pid)
    match = next((a for a in accounts if a.get("platform") == platform
                  and _profile_of(a) == pid and a.get("_id")), None)
    if not match:
        raise HTTPException(status_code=422, detail="zernio_account_not_in_profile")  # no cayó acá → no guarda
    aid = str(match.get("_id"))
    handle = match.get("username") or match.get("displayName")   # autoritativo de Zernio (ignora cualquier body)
    sb = get_supabase_service().client
    existing = (sb.table("social_accounts").select("id")
                .eq("client_id", client_id).eq("platform", platform).limit(1).execute().data)
    payload = {"zernio_account_id": aid, "zernio_account_handle": handle,
               "oauth_status": "connected", "status": "active"}
    if existing:
        sb.table("social_accounts").update(payload).eq("id", existing[0]["id"]).execute()
    else:
        sb.table("social_accounts").insert({**payload, "client_id": client_id,
                                            "platform": platform, "account_name": handle or aid}).execute()
    return {"ok": True, "zernio_account_id": aid, "handle": handle}
