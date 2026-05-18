"""
Social Account Domain Models
Pydantic schemas for social account management.
Zero business logic. Zero infrastructure imports.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime

# ── Literal types ──────────────────────────────────────────
PlatformOption = Literal[
    "instagram",
    "facebook",
    "twitter",
    "linkedin",
    "tiktok",
    "youtube",
    "pinterest"
]

# ── Data shape (DB row) ────────────────────────────────────
class SocialAccountProfile(BaseModel):
    """
    Complete social account profile from database.
    """
    id: str
    client_id: str
    platform: PlatformOption
    username: str
    profile_url: Optional[str] = None
    context_id: Optional[str] = None
    scraping_enabled: bool = True
    scraped_data: Optional[dict] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ── Create payload ─────────────────────────────────────────
class SocialAccountCreate(BaseModel):
    """Request payload for creating new social account"""
    client_id: str = Field(..., description="Client UUID")
    platform: PlatformOption = Field(..., description="Social media platform")
    username: str = Field(..., min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context_id: Optional[str] = Field(
        default=None,
        description="Optional context UUID for platform-specific context"
    )

# ── Update payload (all Optional) ──────────────────────────
class SocialAccountUpdate(BaseModel):
    """Request payload for updating existing social account"""
    username: Optional[str] = Field(default=None, min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context_id: Optional[str] = None
    scraping_enabled: Optional[bool] = None
    scraped_data: Optional[dict] = None
    is_active: Optional[bool] = None

# ── Response envelopes ─────────────────────────────────────
class SocialAccountResponse(BaseModel):
    """Standard API response for single social account operations"""
    success: bool
    data: Optional[SocialAccountProfile] = None
    message: Optional[str] = None
    error: Optional[str] = None

class SocialAccountListResponse(BaseModel):
    """API response for list operations"""
    success: bool
    data: List[SocialAccountProfile] = Field(default_factory=list)
    total: int = 0
    message: Optional[str] = None
    error: Optional[str] = None
