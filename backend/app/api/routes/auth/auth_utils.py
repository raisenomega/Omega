"""
Auth Helper Utilities
Extended authentication helpers for role-based access control
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException
import jwt
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# DEBT-028: leer JWT_SECRET via settings; fail-fast cubierto por Settings()
JWT_SECRET = settings.jwt_secret_key
JWT_ALGORITHM = "HS256"


async def get_current_user(authorization: Optional[str]) -> Dict[str, Any]:
    """
    Extract and verify full user data from Authorization header

    Args:
        authorization: Authorization header value ("Bearer <token>")

    Returns:
        Dict with: id, email, role, reseller_id from verified token

    Raises:
        HTTPException 401: Missing or invalid authorization header

    Used for role-based access control in endpoints that need to
    check user permissions beyond just identity verification.
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )

    token = authorization.replace("Bearer ", "").strip()

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type. Expected access token."
            )

        return {
            "id": payload.get("sub") or payload.get("id"),
            "email": payload.get("email"),
            "role": payload.get("role", "client"),
            "reseller_id": payload.get("reseller_id"),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid access token: {e}")
        raise HTTPException(status_code=401, detail="Invalid access token")
