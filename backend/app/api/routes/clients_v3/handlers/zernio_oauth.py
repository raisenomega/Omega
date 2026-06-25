"""B-2 · profile + connect-url + estado de conexión por negocio (aislado · white-label).
Guard = user_owns_client en CADA endpoint ANTES de tocar nada (service_role bypassa RLS).
La etiqueta cara-cliente sale del platform de la red ('Zernio' nunca en pantalla)."""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.clients_v3 import _clients_reader as reader, _clients_repository as repo
from app.api.routes.clients_v3._access_control import user_owns_client
from app.api.routes.clients_v3._zernio_state import sign_state, build_callback_url
from app.api.routes.clients_v3._zernio_http import zernio_error_to_http
from app.bc_cognition.infrastructure.zernio_adapter import list_accounts, ZernioError
from app.bc_cognition.infrastructure.zernio_profiles import get_or_create_profile, get_connect_url
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def _account_followers(account: dict, profile_id: str) -> Optional[int]:
    """followersCount REAL solo si el account es de ESTE profile (aislamiento · NUNCA page_follows).
    None si no casa o falta dato → la UI muestra '—', JAMÁS 0 inventado (P1 · cero sintético)."""
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


_NAME_BASE_MAX = 40  # B2.5 Capa B · cap del nombre legible · el uuid (36) SIEMPRE entra intacto


def _profile_name(client: dict, client_id: str) -> str:
    """Nombre ÚNICO por negocio (B2.5 Capa B): client_id (PK) → dos homónimos nunca colisionan.
    Base truncada (cualquier nombre conecta) · uuid intacto · INTERNO a Zernio (white-label)."""
    base = (client.get("name") or "").strip()[:_NAME_BASE_MAX]
    return f"{base} · {client_id}" if base else client_id


async def _ensure_profile(client_id: str, client: dict) -> str:
    """zernio_profile_id del negocio · crea (nombre único + idempotente) + persiste si falta · cierra huérfanos."""
    pid = client.get("zernio_profile_id")
    if pid:
        return str(pid)
    pid = await get_or_create_profile(_profile_name(client, client_id))
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
    user, client = await _owned(client_id, authorization)  # 404/403 quedan FUERA del try (ya correctos)
    # B2.5 Capa A · fallo de Zernio → HTTP honesto (no 500 crudo · ej. nombre duplicado → 409).
    try:
        pid = await _ensure_profile(client_id, client)
        # Origin firmado solo si ya está permitido (si no → "" → callback usa cors_origins_list[0]).
        safe_origin = origin if (origin and origin in settings.cors_origins_list) else ""
        redirect_url = build_callback_url(sign_state(client_id, platform, safe_origin, str(user["id"])))
        return {"auth_url": await get_connect_url(platform, pid, redirect_url)}
    except ZernioError as e:
        logger.warning("zernio connect-url failed · client=%s platform=%s · %s", client_id, platform, e)
        raise zernio_error_to_http(e) from e


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
