"""
Shared API Models
Generic models used across multiple modules
"""
from pydantic import BaseModel
from typing import Optional, Any


class APIResponse(BaseModel):
    """
    Standard API response wrapper

    Used by all API endpoints for consistent response format

    Attributes:
        success: Boolean indicating request success
        data: Optional response payload
        message: Optional human-readable message
        token: Optional JWT token (auth endpoints)
        refresh_token: Optional refresh token (auth endpoints)
        error: Optional error code for failed requests
    """
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    error: Optional[str] = None
