"""B-2 headless · firma/verifica el `state` del callback de Zernio (el redirect llega SIN JWT).
Espejo de _sign_state/_verify_state de oauth/google_oauth · reusa OAUTH_ENCRYPTION_KEY (HMAC-SHA256).
Codifica client_id+platform+nonce. El callback confía en client_id/platform SOLO si la firma valida
(CSRF/forgery guard · constant-time). Sin la key → CryptoNotConfigured (503 honesto · jamás inseguro)."""
import hashlib
import hmac
import secrets
from typing import Optional

from app.api.routes.oauth._oauth_config import get_oauth_settings
from app.api.routes.oauth._token_crypto import CryptoNotConfigured
from app.config import settings


def _signing_key() -> bytes:
    key = get_oauth_settings().oauth_encryption_key.strip()
    if not key:
        raise CryptoNotConfigured("OAUTH_ENCRYPTION_KEY no configurada")
    return key.encode()


def _msg(client_id: str, platform: str, nonce: str) -> bytes:
    return f"{client_id}:{platform}:{nonce}".encode()


def sign_state(client_id: str, platform: str) -> str:
    """f'{client_id}.{platform}.{nonce}.{sig}' · sig = HMAC-SHA256(key, 'client_id:platform:nonce')."""
    nonce = secrets.token_urlsafe(16)
    sig = hmac.new(_signing_key(), _msg(client_id, platform, nonce), hashlib.sha256).hexdigest()
    return f"{client_id}.{platform}.{nonce}.{sig}"


def verify_state(state: str) -> Optional[tuple[str, str]]:
    """Verifica la firma → (client_id, platform), o None si no valida (CSRF/forgery guard)."""
    parts = state.split(".")
    if len(parts) != 4:
        return None
    client_id, platform, nonce, sig = parts
    expected = hmac.new(_signing_key(), _msg(client_id, platform, nonce), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):  # constant-time
        return None
    return client_id, platform


def build_callback_url(st: str) -> str:
    """URL de retorno del headless (a NUESTRO backend) con el state firmado · base = OAUTH_REDIRECT_BASE."""
    base = get_oauth_settings().oauth_redirect_base.rstrip("/")
    return f"{base}{settings.api_v1_prefix}/clients/zernio/callback?st={st}"
