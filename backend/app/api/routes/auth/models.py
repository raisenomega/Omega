"""
Auth Request Models
Pydantic models for authentication endpoints
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """
    Register new client account

    Attributes:
        name: Client full name
        email: Client email (must be unique)
        password: Password (min 8 characters, validated in endpoint)
        plan: Subscription plan (basic/pro/enterprise)
        reseller_id: Optional reseller UUID for white-label clients
    """
    name: str = Field(..., min_length=2, max_length=255, description="Client full name")
    email: EmailStr = Field(..., description="Client email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    plan: str = Field(default="basic", description="Subscription plan")
    reseller_id: Optional[str] = Field(None, description="Optional reseller UUID")


class LoginRequest(BaseModel):
    """
    Login request with email and password

    Attributes:
        email: Client email address
        password: Client password (verified with bcrypt)
    """
    email: EmailStr = Field(..., description="Client email address")
    password: str = Field(..., description="Client password")


class RefreshTokenRequest(BaseModel):
    """
    Refresh JWT access token request

    Attributes:
        refresh_token: Valid refresh token (30 day expiration)
    """
    refresh_token: str = Field(..., description="Valid refresh token")
