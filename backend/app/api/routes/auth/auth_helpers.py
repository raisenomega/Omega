"""Auth helper utilities: user extraction and role routing"""
from typing import Optional
from fastapi import HTTPException
from .jwt_token_utils import verify_access_token


async def get_current_user_id(authorization: Optional[str]) -> str:
    """Extract and verify client_id from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Expected 'Bearer <token>'",
        )
    token = authorization.replace("Bearer ", "").strip()
    return verify_access_token(token)


def get_redirect_by_role(role: str) -> str:
    """Get frontend redirect path based on user role"""
    role_redirects = {
        "client": "/dashboard",
        "reseller": "/reseller/dashboard",
        "owner": "/admin/resellers",
        "agent": "/dashboard",
    }
    return role_redirects.get(role, "/dashboard")
