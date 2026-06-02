"""Pydantic models · GET /clients/{id}/social-accounts (DEBT-CL-015).

Response shape sin tokens (security · cero access_token/refresh_token leak).
"""
from typing import Optional
from pydantic import BaseModel, Field


class SocialAccountSummary(BaseModel):
    id: str
    platform: str
    account_name: str
    status: str  # active|expired|disconnected
    zernio_account_id: Optional[str] = None        # F5/2b · mapeo persistido
    zernio_account_handle: Optional[str] = None


class SocialAccountListResponse(BaseModel):
    items: list[SocialAccountSummary]
    total: int


class ZernioMapRequest(BaseModel):
    zernio_account_id: str = Field(..., min_length=1, max_length=128)
    zernio_account_handle: Optional[str] = Field(default=None, max_length=128)


class ZernioAvailableAccount(BaseModel):
    zernio_account_id: str
    platform: str
    handle: Optional[str] = None


class ZernioAvailableResponse(BaseModel):
    items: list[ZernioAvailableAccount]
    total: int
