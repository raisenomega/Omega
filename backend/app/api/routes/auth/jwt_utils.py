"""
Auth JWT Utilities — re-export module (backward compat).
Logic lives in:
  jwt_token_utils.py  — token creation/verification
  password_utils.py   — bcrypt hashing
  auth_helpers.py     — get_current_user_id, get_redirect_by_role
"""
from .jwt_token_utils import (
    JWT_SECRET,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_DAYS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from .password_utils import hash_password, verify_password
from .auth_helpers import get_current_user_id, get_redirect_by_role

__all__ = [
    "JWT_SECRET", "JWT_ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_DAYS", "REFRESH_TOKEN_EXPIRE_DAYS",
    "create_access_token", "create_refresh_token",
    "verify_access_token", "verify_refresh_token",
    "hash_password", "verify_password",
    "get_current_user_id", "get_redirect_by_role",
]
