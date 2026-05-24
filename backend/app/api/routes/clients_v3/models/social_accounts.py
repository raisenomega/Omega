"""Pydantic models · GET /clients/{id}/social-accounts (DEBT-CL-015).

Response shape sin tokens (security · cero access_token/refresh_token leak).
"""
from typing import Optional
from pydantic import BaseModel


class SocialAccountSummary(BaseModel):
    id: str
    platform: str
    account_name: str
    status: str  # active|expired|disconnected


class SocialAccountListResponse(BaseModel):
    items: list[SocialAccountSummary]
    total: int
