"""Auth · Supabase JWT (ES256/RS256 via JWKS) primero · fallback local HS256."""
from typing import Optional, Dict, Any
from fastapi import HTTPException
import jwt
from jwt import PyJWKClient
import logging

from app.config import settings

logger = logging.getLogger(__name__)
JWT_LOCAL_ALG = "HS256"

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
    try:
        from app.infrastructure.supabase_service import get_supabase_service
        sb = get_supabase_service().client
        r = sb.table("resellers").select("id, is_owner").eq("owner_user_id", user_id).limit(1).execute()
        if r.data:
            row = r.data[0]
            return ("owner" if row.get("is_owner") else "reseller", str(row["id"]))
        return ("client", None)  # cliente o sin fila → 'client' (1 sola query)
    except Exception as e:
        logger.error(f"_resolve_role_and_reseller failed ({user_id}): {e}")
        return ("client", None)  # fail-closed: menor privilegio ante fallo


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
