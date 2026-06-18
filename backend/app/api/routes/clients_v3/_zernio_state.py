"""B-2 headless · firma/verifica el `state` del callback de Zernio (el redirect llega SIN JWT).
Espejo de _sign_state/_verify_state de oauth/google_oauth · reusa OAUTH_ENCRYPTION_KEY (HMAC-SHA256).
Codifica client_id+platform+origin+nonce. El callback confía en esos campos SOLO si la firma valida
(CSRF/forgery guard · constant-time). El origen se firma para volver al MISMO dominio del usuario (www
vs non-www); IGUAL se RE-VALIDA contra la allowlist en el callback. Sin la key → CryptoNotConfigured."""
import base64
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


def _enc(origin: str) -> str:
    """base64url SIN padding del origen → cero '.' y cero '=' (seguro para el separador y para URLs)."""
    return base64.urlsafe_b64encode(origin.encode()).decode().rstrip("=")


def _dec(b64: str) -> str:
    try:
        return base64.urlsafe_b64decode((b64 + "=" * (-len(b64) % 4)).encode()).decode()
    except Exception:
        return ""


def _msg(client_id: str, platform: str, o: str, nonce: str) -> bytes:
    return f"{client_id}:{platform}:{o}:{nonce}".encode()


def sign_state(client_id: str, platform: str, origin: str = "") -> str:
    """f'{client_id}.{platform}.{b64origin}.{nonce}.{sig}' · sig = HMAC-SHA256(key, 'cid:plat:o:nonce')."""
    nonce = secrets.token_urlsafe(16)
    o = _enc(origin)
    sig = hmac.new(_signing_key(), _msg(client_id, platform, o, nonce), hashlib.sha256).hexdigest()
    return f"{client_id}.{platform}.{o}.{nonce}.{sig}"


def verify_state(state: str) -> Optional[tuple[str, str, str]]:
    """Verifica la firma → (client_id, platform, origin), o None si no valida (CSRF/forgery guard)."""
    parts = state.split(".")
    if len(parts) != 5:
        return None
    client_id, platform, o, nonce, sig = parts
    expected = hmac.new(_signing_key(), _msg(client_id, platform, o, nonce), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):  # constant-time
        return None
    return client_id, platform, _dec(o)


def build_callback_url(st: str) -> str:
    """URL de retorno del headless (a NUESTRO backend) con el state firmado · base = OAUTH_REDIRECT_BASE."""
    base = get_oauth_settings().oauth_redirect_base.rstrip("/")
    return f"{base}{settings.api_v1_prefix}/clients/zernio/callback?st={st}"
