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
from app.config import settings

router = APIRouter()


def _account_followers(account: dict, profile_id: str) -> Optional[int]:
    """followersCount REAL del account SOLO si pertenece a ESTE profile (aislamiento · mismo
    criterio que _analytics_assembler.followers_total · NUNCA page_follows). None si el profile
    no casa o no hay dato → la fila muestra '—', JAMÁS 0 inventado: el número real de Zernio es
    la única fuente (P1 · cero sintético)."""
    p = account.get("profileId")
    acc_pid = str(p.get("_id")) if isinstance(p, dict) else (str(p) if p else None)
    if acc_pid != profile_id:
        return None
    fc = account.get("followersCount")
    return int(fc) if fc is not None else None


async def _owned(client_id: str, authorization: Optional[str]) -> tuple[dict, dict]:
    """Devuelve (user, client) · 403 si el user autenticado no es dueño. El user_id se propaga al state
    firmado (connect-url) para atar el stash FB a quien inició el flujo (defensa-en-profundidad)."""
    user = await get_current_user(authorization)
    client = reader.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="client_not_found")
    if not user_owns_client(user["id"], client):
        raise HTTPException(status_code=403, detail="client_access_denied")
    return user, client


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
    _, client = await _owned(client_id, authorization)
    return {"zernio_profile_id": await _ensure_profile(client_id, client)}


@router.get("/{client_id}/social-accounts/{platform}/connect-url")
async def zernio_connect_url(client_id: str, platform: str,
                             authorization: Optional[str] = Header(None),
                             origin: Optional[str] = Header(None)) -> dict:
    user, client = await _owned(client_id, authorization)  # JWT + ownership ANTES de firmar el state
    pid = await _ensure_profile(client_id, client)
    # firmamos el Origin del navegador SOLO si ya está permitido (si falta/no permitido → "" → callback usa [0]).
    safe_origin = origin if (origin and origin in settings.cors_origins_list) else ""
    # user_id FIRMADO en el state → el callback ata el stash FB a quien inició el flujo (defensa-en-profundidad).
    redirect_url = build_callback_url(sign_state(client_id, platform, safe_origin, str(user["id"])))
    return {"auth_url": await get_connect_url(platform, pid, redirect_url)}


@router.get("/{client_id}/connected-accounts")
async def zernio_connected_accounts(client_id: str,
                                    authorization: Optional[str] = Header(None)) -> dict:
    _, client = await _owned(client_id, authorization)
    pid = client.get("zernio_profile_id")
    if not pid:
        return {"profile": None, "items": []}
    accounts = await list_accounts(str(pid))
    items = [{"platform": a.get("platform"),
              "handle": a.get("username") or a.get("displayName"),
              "zernio_account_id": str(a.get("_id")),
              "followers_count": _account_followers(a, str(pid))}  # real de Zernio · None → fila '—'
             for a in accounts if a.get("_id")]
    return {"profile": str(pid), "items": items}
