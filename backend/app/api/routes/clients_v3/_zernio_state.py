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
from urllib.parse import urlparse

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
    """Mensaje firmado LEGACY (5-seg · sin user_id) · solo para back-compat de states en vuelo."""
    return f"{client_id}:{platform}:{o}:{nonce}".encode()


def _msgu(client_id: str, platform: str, o: str, user_id: str, nonce: str) -> bytes:
    """Mensaje firmado ACTUAL (6-seg · con user_id · defensa-en-profundidad del stash FB)."""
    return f"{client_id}:{platform}:{o}:{user_id}:{nonce}".encode()


def sign_state(client_id: str, platform: str, origin: str = "", user_id: str = "") -> str:
    """6 segmentos: '{client_id}.{platform}.{b64origin}.{user_id}.{nonce}.{sig}'. El user_id va FIRMADO en
    el HMAC (inforjable · ata el stash FB a quien inicio el flujo · UUID sin puntos → split seguro)."""
    nonce = secrets.token_urlsafe(16)
    o = _enc(origin)
    sig = hmac.new(_signing_key(), _msgu(client_id, platform, o, user_id, nonce), hashlib.sha256).hexdigest()
    return f"{client_id}.{platform}.{o}.{user_id}.{nonce}.{sig}"


def verify_state(state: str) -> Optional[tuple[str, str, str, str]]:
    """Verifica la firma → (client_id, platform, origin, user_id), o None si no valida. TOLERA 5-seg
    (LEGACY · user_id='') por BACK-COMPAT de states en vuelo durante el deploy (efimeros · branch
    transitorio · removible cuando pase la ventana de deploy)."""
    parts = state.split(".")
    if len(parts) == 6:
        client_id, platform, o, user_id, nonce, sig = parts
        exp = hmac.new(_signing_key(), _msgu(client_id, platform, o, user_id, nonce), hashlib.sha256).hexdigest()
        return (client_id, platform, _dec(o), user_id) if hmac.compare_digest(sig, exp) else None
    if len(parts) == 5:   # LEGACY en vuelo (firmado por el deploy anterior · sin user_id)
        client_id, platform, o, nonce, sig = parts
        exp = hmac.new(_signing_key(), _msg(client_id, platform, o, nonce), hashlib.sha256).hexdigest()
        return (client_id, platform, _dec(o), "") if hmac.compare_digest(sig, exp) else None
    return None


def build_callback_url(st: str) -> str:
    """URL de retorno del headless (a NUESTRO backend) con el state firmado. Deriva la base con urlparse
    → scheme://netloc (DESCARTA cualquier path pegado a OAUTH_REDIRECT_BASE). Si la base no tiene
    scheme(http/https)+host válido (vacía/relativa), RAISE ruidoso: Zernio rechaza un redirectUrl relativo
    (400 → 500 silencioso con un cliente). Mejor fallar claro en deploy/test (cubierto por test) que en runtime."""
    raw = get_oauth_settings().oauth_redirect_base.strip()
    p = urlparse(raw)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise RuntimeError(f"OAUTH_REDIRECT_BASE inválida o ausente: {raw!r}")
    return f"{p.scheme}://{p.netloc}{settings.api_v1_prefix}/clients/zernio/callback?st={st}"
