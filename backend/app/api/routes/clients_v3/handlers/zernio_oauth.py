"""B-2 · profile + OAuth connect URL + estado real de conexión (por negocio · aislado).

Cada negocio = un profile Zernio. getConnectUrl es profile-scoped → la red que el cliente
autoriza cae en SU profile. SEGURIDAD: get_supabase_service usa service_role → BYPASSA RLS;
el guard es user_owns_client en CADA endpoint ANTES de tocar nada (igual que zernio_mapping).
La etiqueta cara-cliente sale del platform de la red (white-label · 'Zernio' nunca en pantalla).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader, _clients_repository as repo
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3._zernio_state import sign_state, build_callback_url
from app.bc_cognition.infrastructure.zernio_adapter import list_accounts
from app.bc_cognition.infrastructure.zernio_profiles import create_profile, get_connect_url

router = APIRouter()


async def _owned(client_id: str, authorization: Optional[str]) -> dict:
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="client_access_denied")
    return client


async def _ensure_profile(client_id: str, client: dict) -> str:
    """Devuelve el zernio_profile_id del negocio · lo crea (POST /profiles) y persiste si falta."""
    pid = client.get("zernio_profile_id")
    if pid:
        return str(pid)
    pid = await create_profile(client.get("name") or client_id)
    repo.update_client_by_id(client_id, {"zernio_profile_id": pid})
    return pid


@router.post("/{client_id}/zernio-profile")
async def ensure_zernio_profile(client_id: str, authorization: Optional[str] = Header(None)) -> dict:
    client = await _owned(client_id, authorization)
    return {"zernio_profile_id": await _ensure_profile(client_id, client)}


@router.get("/{client_id}/social-accounts/{platform}/connect-url")
async def zernio_connect_url(client_id: str, platform: str,
                             authorization: Optional[str] = Header(None)) -> dict:
    client = await _owned(client_id, authorization)        # JWT + ownership ANTES de firmar el state
    pid = await _ensure_profile(client_id, client)
    redirect_url = build_callback_url(sign_state(client_id, platform))   # HEADLESS · vuelve a OMEGA
    return {"auth_url": await get_connect_url(platform, pid, redirect_url)}


@router.get("/{client_id}/connected-accounts")
async def zernio_connected_accounts(client_id: str,
                                    authorization: Optional[str] = Header(None)) -> dict:
    client = await _owned(client_id, authorization)
    pid = client.get("zernio_profile_id")
    if not pid:
        return {"profile": None, "items": []}
    accounts = await list_accounts(str(pid))
    items = [{"platform": a.get("platform"),
              "handle": a.get("username") or a.get("displayName"),
              "zernio_account_id": str(a.get("_id"))} for a in accounts if a.get("_id")]
    return {"profile": str(pid), "items": items}
