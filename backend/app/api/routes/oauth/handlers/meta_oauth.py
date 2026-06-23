"""Meta (Facebook/Instagram) OAuth flow per cliente (RONDA D).

3 endpoints montados bajo /oauth por el orquestador:
  GET /meta/authorize  (JWT) → URL del dialog OAuth con state firmado (CSRF).
  GET /meta/callback    (sin JWT · Meta redirige) → exchange code → store_token → redirect.
  GET /meta/status      (JWT) → {connected, scopes, external_account_id}.

503 honesto: sin META_APP_ID/SECRET ("meta_not_configured") o sin OAUTH_ENCRYPTION_KEY
("crypto_not_configured"). NUNCA se fabrica una conexión (regla cero-mocks).
Tokens long-lived de Meta duran ~60 días → refresh_meta_token (best-effort, fb_exchange_token).
"""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.oauth._oauth_config import get_oauth_settings
from app.api.routes.oauth._oauth_token_repository import get_token, store_token

router = APIRouter()
logger = logging.getLogger(__name__)

_GRAPH_VERSION = "v21.0"
_DIALOG_URL = f"https://www.facebook.com/{_GRAPH_VERSION}/dialog/oauth"
_TOKEN_URL = f"https://graph.facebook.com/{_GRAPH_VERSION}/oauth/access_token"
_ACCOUNTS_URL = f"https://graph.facebook.com/{_GRAPH_VERSION}/me/accounts"
_SCOPES = (
    "pages_show_list,pages_read_engagement,pages_manage_posts,"
    "instagram_basic,instagram_content_publish"
)
_CALLBACK_PATH = "/api/v1/oauth/meta/callback"
_HTTP_TIMEOUT = 15.0


def _redirect_uri() -> str:
    """URI de callback registrada en la app de Meta (sin trailing slash en base)."""
    base = get_oauth_settings().oauth_redirect_base.rstrip("/")
    return f"{base}{_CALLBACK_PATH}"


def _signing_key() -> bytes:
    """Clave HMAC para firmar el state · reusa OAUTH_ENCRYPTION_KEY (503 si vacía)."""
    key = get_oauth_settings().oauth_encryption_key.strip()
    if not key:
        raise HTTPException(status_code=503, detail="crypto_not_configured")
    return key.encode()


def _sign_state(client_id: str) -> str:
    """state = client_id.nonce.sig · sig = HMAC-SHA256(key, "client_id:nonce"). CSRF-proof."""
    nonce = secrets.token_urlsafe(16)
    sig = hmac.new(_signing_key(), f"{client_id}:{nonce}".encode(), hashlib.sha256).hexdigest()
    return f"{client_id}.{nonce}.{sig}"


def _verify_state(state: str) -> str:
    """Verifica el state firmado y devuelve el client_id. Lanza 400 si es inválido."""
    parts = state.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=400, detail="invalid_state")
    client_id, nonce, sig = parts
    expected = hmac.new(_signing_key(), f"{client_id}:{nonce}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):  # comparación tiempo-constante
        raise HTTPException(status_code=400, detail="invalid_state")
    return client_id


async def _owned_client_id(client_id: str, authorization: Optional[str]) -> str:
    """client_id del Switcher + ownership verbatim (resolve_client_or_403 · get_client+user_owns_client).
    404 si no existe · 403 si ajeno. Aísla: nadie conecta Meta de un negocio que no es suyo."""
    user = await get_current_user(authorization)
    return str(resolve_client_or_403(user["id"], client_id)["id"])


def _expires_at_iso(expires_in: Optional[int]) -> Optional[str]:
    """Convierte expires_in (segundos) a timestamp ISO UTC absoluto. None si no viene."""
    if not expires_in:
        return None
    return (datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))).isoformat()


@router.get("/meta/authorize")
async def meta_authorize(client_id: str = Query(...),
                         authorization: Optional[str] = Header(None)) -> dict[str, str]:
    """Construye la URL del dialog OAuth de Meta con state firmado. 503 honesto sin credenciales."""
    settings = get_oauth_settings()
    if not settings.meta_app_id or not settings.meta_app_secret:
        raise HTTPException(status_code=503, detail="meta_not_configured")
    actor_client_id = await _owned_client_id(client_id, authorization)
    state = _sign_state(actor_client_id)  # 503 crypto_not_configured si no hay key
    params = {
        "client_id": settings.meta_app_id,
        "redirect_uri": _redirect_uri(),
        "scope": _SCOPES,
        "state": state,
        "response_type": "code",
    }
    query = httpx.QueryParams(params)
    return {"authorize_url": f"{_DIALOG_URL}?{query}"}


async def _exchange_code(code: str) -> dict[str, object]:
    """Intercambia el authorization code por un access_token. Lanza 502 en error de Graph."""
    settings = get_oauth_settings()
    params = {
        "client_id": settings.meta_app_id,
        "client_secret": settings.meta_app_secret,
        "redirect_uri": _redirect_uri(),
        "code": code,
    }
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
        resp = await client.get(_TOKEN_URL, params=params)
    if resp.status_code != 200:
        logger.warning(f"meta token exchange failed · {resp.status_code} · {resp.text[:200]}")
        raise HTTPException(status_code=502, detail="meta_exchange_failed")
    return resp.json()


async def _fetch_page_id(access_token: str) -> Optional[str]:
    """Best-effort: primer page id de /me/accounts → external_account_id. None si falla."""
    try:
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(_ACCOUNTS_URL, params={"access_token": access_token})
        if resp.status_code != 200:
            return None
        data = resp.json().get("data") or []
        return str(data[0]["id"]) if data else None
    except Exception as e:  # noqa: BLE001 · best-effort, jamás bloquea el connect
        logger.info(f"meta /me/accounts skip · {e}")
        return None


@router.get("/meta/callback")
async def meta_callback(
    code: str = Query(...),
    state: str = Query(...),
) -> RedirectResponse:
    """Meta redirige aquí (sin JWT). Verifica state, exchange code, persiste token, redirige."""
    settings = get_oauth_settings()
    if not settings.meta_app_id or not settings.meta_app_secret:
        raise HTTPException(status_code=503, detail="meta_not_configured")
    client_id = _verify_state(state)  # 400 si state inválido · 503 si no hay crypto key
    front_base = settings.oauth_redirect_base.rstrip("/")
    try:
        token_data = await _exchange_code(code)
        access_token = str(token_data.get("access_token") or "")
        if not access_token:
            raise HTTPException(status_code=502, detail="meta_no_access_token")
        expires_in = token_data.get("expires_in")
        expires_at = _expires_at_iso(int(expires_in) if isinstance(expires_in, (int, float)) else None)
        page_id = await _fetch_page_id(access_token)
        await store_token(
            client_id, "meta", access_token,
            expires_at=expires_at, scopes=_SCOPES, external_account_id=page_id,
        )
    except HTTPException:
        return RedirectResponse(url=f"{front_base}/settings?oauth_error=meta", status_code=302)
    except Exception as e:  # noqa: BLE001 · cualquier fallo → redirect honesto (no 500 a Meta)
        logger.error(f"meta callback failed · {e}")
        return RedirectResponse(url=f"{front_base}/settings?oauth_error=meta", status_code=302)
    return RedirectResponse(url=f"{front_base}/settings?connected=meta", status_code=302)


@router.get("/meta/status")
async def meta_status(client_id: str = Query(...),
                      authorization: Optional[str] = Header(None)) -> dict[str, object]:
    """Estado de la conexión Meta del cliente. Nunca 500: fallo de decrypt/creds → connected:false."""
    actor_client_id = await _owned_client_id(client_id, authorization)
    try:
        token = await get_token(actor_client_id, "meta")
    except Exception as e:  # noqa: BLE001 · CryptoNotConfigured / decrypt fail → honesto
        logger.info(f"meta status read failed · {e}")
        return {"connected": False, "scopes": None, "external_account_id": None}
    if not token:
        return {"connected": False, "scopes": None, "external_account_id": None}
    return {
        "connected": True,
        "scopes": token.get("scopes"),
        "external_account_id": token.get("external_account_id"),
    }


async def refresh_meta_token(client_id: str) -> Optional[str]:
    """Best-effort: intercambia el token corto por uno long-lived (~60 días · fb_exchange_token).

    Meta no usa refresh_token clásico: se re-extiende el access_token vigente con
    grant_type=fb_exchange_token. Devuelve el nuevo access_token o None si no se pudo.
    NO levanta excepciones (caller decide reconectar si vuelve None).
    """
    settings = get_oauth_settings()
    if not settings.meta_app_id or not settings.meta_app_secret:
        return None
    try:
        current = await get_token(client_id, "meta")
        if not current or not current.get("access_token"):
            return None
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": settings.meta_app_id,
            "client_secret": settings.meta_app_secret,
            "fb_exchange_token": current["access_token"],
        }
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
            resp = await client.get(_TOKEN_URL, params=params)
        if resp.status_code != 200:
            logger.warning(f"meta refresh failed · {resp.status_code} · {resp.text[:200]}")
            return None
        data = resp.json()
        new_token = str(data.get("access_token") or "")
        if not new_token:
            return None
        expires_in = data.get("expires_in")
        expires_at = _expires_at_iso(int(expires_in) if isinstance(expires_in, (int, float)) else None)
        await store_token(
            client_id, "meta", new_token,
            expires_at=expires_at, scopes=current.get("scopes"),
            external_account_id=current.get("external_account_id"),
        )
        return new_token
    except Exception as e:  # noqa: BLE001 · best-effort, jamás propaga
        logger.error(f"meta refresh exception · {e}")
        return None
