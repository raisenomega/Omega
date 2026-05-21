"""Auth Helper Utilities · valida JWT de Supabase O JWT local legacy.

Producción: el frontend usa supabase.auth.getSession() · el token está
firmado con SUPABASE_JWT_SECRET (HS256 default Supabase Auth).
Dev local sin Supabase JWT: cae al JWT_SECRET_KEY local emitido por
/api/v1/auth/login (claim type='access' obligatorio).
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException
import jwt
import logging

from app.config import settings

logger = logging.getLogger(__name__)
JWT_ALGORITHM = "HS256"


def _decode_supabase(token: str) -> Optional[Dict[str, Any]]:
    """Intenta decodificar con SUPABASE_JWT_SECRET · None si no aplica."""
    if not settings.supabase_jwt_secret:
        return None
    try:
        return jwt.decode(
            token, settings.supabase_jwt_secret,
            algorithms=[JWT_ALGORITHM],
            options={"verify_aud": False},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        return None  # firma no matchea · probar JWT local


def _decode_local(token: str) -> Dict[str, Any]:
    """Decodifica con JWT_SECRET_KEY local · requiere claim type='access'."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type. Expected access token.")
    return payload


async def get_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    """Extrae user desde Authorization Bearer · Supabase first, local fallback."""
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
