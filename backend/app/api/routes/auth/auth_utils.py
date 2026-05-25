"""Auth · Supabase JWT (ES256/RS256 via JWKS) primero · fallback local HS256."""
from typing import Optional, Dict, Any
from fastapi import HTTPException
import jwt
from jwt import PyJWKClient
import logging
import time
import threading

from app.config import settings

logger = logging.getLogger(__name__)
JWT_LOCAL_ALG = "HS256"

# Caché TTL-corto del rol derivado (per-process · no compartido entre workers) · evita 1 query/request.
# TRADE-OFF: un upgrade O una revocación de rol tarda hasta _ROLE_CACHE_TTL en reflejarse.
_ROLE_CACHE_TTL = 60.0  # segundos
_role_cache: Dict[str, tuple[float, str, Optional[str]]] = {}  # user_id → (expires_at, role, reseller_id)
_role_cache_lock = threading.Lock()

# JWKS client cached at module level · PyJWKClient cachea las signing keys
# internamente (cache_keys=True default, lifespan 300s).
SUPABASE_JWKS_URL = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
_jwks_client = PyJWKClient(SUPABASE_JWKS_URL)


def _decode_supabase(token: str) -> Optional[Dict[str, Any]]:
    """Verifica con clave pública Supabase via JWKS · ES256 actual + RS256 fallback."""
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=["ES256", "RS256"], options={"verify_aud": False})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.debug(f"Supabase JWT decode failed (probará local): {e}")
        return None


def _decode_local(token: str) -> Dict[str, Any]:
    """Decodifica con JWT_SECRET_KEY local · requiere claim type='access'."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_LOCAL_ALG])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type. Expected access token.")
    return payload


def _resolve_role_and_reseller(user_id: Optional[str]) -> tuple[str, Optional[str]]:
    """Deriva (role, reseller_id) desde la DB · forgery-proof: NO confía en claims del JWT
    (user_metadata es editable por el usuario → escalada de privilegios · guardian).
    owner = reseller con is_owner=true (superadmin real · 00022) · reseller = dueño de
    reseller · client = default seguro. Fail-closed a 'client' ante error de DB."""
    if not user_id:
        return ("client", None)
    now = time.monotonic()
    with _role_cache_lock:  # hit de caché (lock breve · sin I/O adentro)
        hit = _role_cache.get(user_id)
        if hit and hit[0] > now:
            return (hit[1], hit[2])
    try:
        from app.infrastructure.supabase_service import get_supabase_service
        sb = get_supabase_service().client
        r = sb.table("resellers").select("id, is_owner").eq("owner_user_id", user_id).limit(1).execute()
        if r.data:
            row = r.data[0]
            result = ("owner" if row.get("is_owner") else "reseller", str(row["id"]))
        else:
            result = ("client", None)  # cliente o sin fila → 'client'
    except Exception as e:
        logger.error(f"_resolve_role_and_reseller failed ({user_id}): {e}")
        return ("client", None)  # fail-closed · NO se cachea el error (reintenta al próximo request)
    with _role_cache_lock:
        if len(_role_cache) > 5000:  # guard de memoria · purga expirados
            for k in [k for k, v in _role_cache.items() if v[0] <= now]:
                _role_cache.pop(k, None)
        _role_cache[user_id] = (now + _ROLE_CACHE_TTL, result[0], result[1])
    return result


async def get_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    """Extrae user desde Authorization Bearer · Supabase RS256 first, local HS256 fallback.
    El role/reseller_id se DERIVAN server-side de la DB (no del claim · forgery-proof)."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Expected 'Bearer <token>'")
    token = authorization.replace("Bearer ", "").strip()

    sb_payload = _decode_supabase(token)
    if sb_payload is not None:
        uid = sb_payload.get("sub")
        role, reseller_id = _resolve_role_and_reseller(uid)
        return {"id": uid, "email": sb_payload.get("email"), "role": role, "reseller_id": reseller_id}

    payload = _decode_local(token)
    uid = payload.get("sub") or payload.get("id")
    role, reseller_id = _resolve_role_and_reseller(uid)
    return {"id": uid, "email": payload.get("email"), "role": role, "reseller_id": reseller_id}
