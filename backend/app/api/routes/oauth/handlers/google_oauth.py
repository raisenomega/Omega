"""Google OAuth (Analytics + Search Console) · RONDA D.

Flujo per cliente: authorize → callback (Google redirige) → token cifrado en oauth_tokens.
Credenciales vacías → 503 honesto (sin app registrada · NUNCA mock). El `state` lleva el
client_id firmado (HMAC-SHA256 con OAUTH_ENCRYPTION_KEY) para CSRF: el callback NO tiene JWT
(lo invoca Google), así que el client_id viaja firmado en el round-trip.

Scopes (read-only): analytics.readonly + webmasters.readonly. access_type=offline + prompt=consent
fuerzan a Google a devolver refresh_token (necesario para refrescar sin re-login del usuario).
"""
import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.oauth._oauth_config import get_oauth_settings
from app.api.routes.oauth._oauth_token_repository import get_token, store_token
from app.api.routes.oauth._token_crypto import CryptoNotConfigured

router = APIRouter()
logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = (
    "https://www.googleapis.com/auth/analytics.readonly "
    "https://www.googleapis.com/auth/webmasters.readonly"
)
_PROVIDER = "google"


def _signing_key() -> bytes:
    """Clave HMAC para firmar el state · reutiliza OAUTH_ENCRYPTION_KEY. Vacía → CryptoNotConfigured."""
    key = get_oauth_settings().oauth_encryption_key.strip()
    if not key:
        raise CryptoNotConfigured("OAUTH_ENCRYPTION_KEY no configurada")
    return key.encode()


def _sign_state(client_id: str) -> str:
    """f'{client_id}.{nonce}.{sig}' · sig = HMAC-SHA256(key, f'{client_id}:{nonce}')."""
    nonce = secrets.token_urlsafe(16)
    sig = hmac.new(_signing_key(), f"{client_id}:{nonce}".encode(), hashlib.sha256).hexdigest()
    return f"{client_id}.{nonce}.{sig}"


def _verify_state(state: str) -> Optional[str]:
    """Verifica el state firmado → client_id, o None si la firma no valida (CSRF guard)."""
    parts = state.split(".")
    if len(parts) != 3:
        return None
    client_id, nonce, sig = parts
    expected = hmac.new(_signing_key(), f"{client_id}:{nonce}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):  # constant-time
        return None
    return client_id


def _redirect_uri() -> str:
    base = get_oauth_settings().oauth_redirect_base.rstrip("/")
    return f"{base}/api/v1/oauth/google/callback"


def _require_google_creds() -> tuple[str, str]:
    """(client_id, client_secret) o 503 honesto si alguna está vacía."""
    s = get_oauth_settings()
    if not s.google_client_id.strip() or not s.google_client_secret.strip():
        raise HTTPException(status_code=503, detail="google_not_configured")
    return s.google_client_id, s.google_client_secret


async def _resolve_client_id(authorization: Optional[str]) -> str:
    """JWT → cliente propio del usuario. 403 si el usuario no tiene cliente."""
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    return str(client["id"])


def _expires_at_iso(expires_in: Optional[int]) -> Optional[str]:
    """expires_in (segundos) → timestamp ISO absoluto. None si Google no lo manda."""
    if not expires_in:
        return None
    return (datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))).isoformat()


@router.get("/google/authorize")
async def google_authorize(authorization: Optional[str] = Header(None)) -> dict[str, str]:
    """Devuelve la URL de consentimiento de Google. 503 honesto sin credenciales/crypto."""
    client_id_app, _ = _require_google_creds()
    actor_client_id = await _resolve_client_id(authorization)
    try:
        state = _sign_state(actor_client_id)
    except CryptoNotConfigured:
        raise HTTPException(status_code=503, detail="crypto_not_configured")

    params = {
        "client_id": client_id_app,
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    authorize_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return {"authorize_url": authorize_url}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
) -> RedirectResponse:
    """Google redirige aquí (sin JWT). Verifica state, canjea code, guarda token cifrado."""
    settings = get_oauth_settings()
    base = settings.oauth_redirect_base.rstrip("/")
    try:
        actor_client_id = _verify_state(state)
    except CryptoNotConfigured:
        raise HTTPException(status_code=503, detail="crypto_not_configured")
    if not actor_client_id:
        raise HTTPException(status_code=400, detail="invalid_state")

    app_client_id, app_client_secret = _require_google_creds()
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(GOOGLE_TOKEN_URL, data={
                "code": code,
                "client_id": app_client_id,
                "client_secret": app_client_secret,
                "redirect_uri": _redirect_uri(),
                "grant_type": "authorization_code",
            })
        if resp.status_code != 200:
            logger.warning(f"google token exchange failed · {resp.status_code} · {resp.text[:200]}")
            return RedirectResponse(url=f"{base}/settings?oauth_error=google", status_code=302)
        token: dict[str, object] = resp.json()
        access_token = str(token.get("access_token") or "")
        if not access_token:
            return RedirectResponse(url=f"{base}/settings?oauth_error=google", status_code=302)
        refresh_token = token.get("refresh_token")
        scope = token.get("scope")
        await store_token(
            actor_client_id, _PROVIDER, access_token,
            refresh_token=str(refresh_token) if refresh_token else None,
            scopes=str(scope) if scope else GOOGLE_SCOPES,
            expires_at=_expires_at_iso(token.get("expires_in") if isinstance(token.get("expires_in"), int) else None),
        )
    except CryptoNotConfigured:
        raise HTTPException(status_code=503, detail="crypto_not_configured")
    except httpx.HTTPError as e:
        logger.warning(f"google callback http error · {e}")
        return RedirectResponse(url=f"{base}/settings?oauth_error=google", status_code=302)

    return RedirectResponse(url=f"{base}/settings?connected=google", status_code=302)


@router.get("/google/status")
async def google_status(authorization: Optional[str] = Header(None)) -> dict[str, object]:
    """Estado de conexión Google del cliente. NUNCA 500 (fail-soft a connected=False)."""
    actor_client_id = await _resolve_client_id(authorization)
    try:
        tok = await get_token(actor_client_id, _PROVIDER)
    except Exception as e:  # crypto/DB → honesto sin tumbar el endpoint
        logger.warning(f"google_status read failed · {e}")
        return {"connected": False, "scopes": None, "has_refresh": False}
    if not tok:
        return {"connected": False, "scopes": None, "has_refresh": False}
    return {
        "connected": True,
        "scopes": tok.get("scopes"),
        "has_refresh": bool(tok.get("refresh_token")),
    }


async def refresh_google_token(client_id: str) -> Optional[str]:
    """Best-effort: refresca el access_token con el refresh_token guardado. Devuelve el nuevo
    access_token o None (sin refresh_token, sin credenciales, o error de Google)."""
    s = get_oauth_settings()
    if not s.google_client_id.strip() or not s.google_client_secret.strip():
        return None
    try:
        tok = await get_token(client_id, _PROVIDER)
    except CryptoNotConfigured:
        return None
    if not tok or not tok.get("refresh_token"):
        return None
    refresh_token = str(tok["refresh_token"])
    try:
        async with httpx.AsyncClient(timeout=15.0) as http:
            resp = await http.post(GOOGLE_TOKEN_URL, data={
                "client_id": s.google_client_id,
                "client_secret": s.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            })
        if resp.status_code != 200:
            logger.warning(f"google refresh failed · {resp.status_code} · {resp.text[:200]}")
            return None
        data: dict[str, object] = resp.json()
        new_access = str(data.get("access_token") or "")
        if not new_access:
            return None
        await store_token(
            client_id, _PROVIDER, new_access,
            refresh_token=refresh_token,  # Google no re-emite refresh en este flujo · conservar
            scopes=tok.get("scopes") if isinstance(tok.get("scopes"), str) else None,
            expires_at=_expires_at_iso(data.get("expires_in") if isinstance(data.get("expires_in"), int) else None),
        )
        return new_access
    except (httpx.HTTPError, CryptoNotConfigured) as e:
        logger.warning(f"google refresh error · {e}")
        return None
