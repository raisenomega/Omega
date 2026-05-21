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


async def get_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    """Extrae user desde Authorization Bearer · Supabase RS256 first, local HS256 fallback."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format. Expected 'Bearer <token>'")
    token = authorization.replace("Bearer ", "").strip()

    sb_payload = _decode_supabase(token)
    if sb_payload is not None:
        meta = sb_payload.get("user_metadata") or {}
        return {
            "id": sb_payload.get("sub"),
            "email": sb_payload.get("email"),
            "role": meta.get("role") or sb_payload.get("role", "client"),
            "reseller_id": meta.get("reseller_id"),
        }

    payload = _decode_local(token)
    return {
        "id": payload.get("sub") or payload.get("id"),
        "email": payload.get("email"),
        "role": payload.get("role", "client"),
        "reseller_id": payload.get("reseller_id"),
    }
