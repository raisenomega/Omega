"""JWT token creation and verification utilities"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import jwt
from fastapi import HTTPException
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# DEBT-028: leer JWT_SECRET via settings; fail-fast ya cubierto por
# Settings(jwt_secret_key=Field(..., env="JWT_SECRET_KEY"))
JWT_SECRET: str = settings.jwt_secret_key

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(client_data: Dict[str, Any]) -> str:
    """Create JWT access token (7-day expiration)"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": client_data["id"],
        "id": client_data["id"],
        "email": client_data["email"],
        "role": client_data.get("role", "client"),
        "reseller_id": client_data.get("reseller_id"),
        "exp": now + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(client_id: str) -> str:
    """Create JWT refresh token (30-day expiration)"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": client_id,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
        "type": "refresh",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> str:
    """Verify JWT access token and return client_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type. Expected access token.")
        client_id = payload.get("sub")
        if not client_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return client_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid access token: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")


def verify_refresh_token(token: str) -> str:
    """Verify JWT refresh token and return client_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type. Expected refresh token.")
        client_id = payload.get("sub")
        if not client_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return client_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid refresh token: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
