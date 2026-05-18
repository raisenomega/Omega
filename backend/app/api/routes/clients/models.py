"""
Client Domain Models
Pydantic schemas for client management.
Zero business logic. Zero infrastructure imports.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from datetime import datetime

# ── Literal types ──────────────────────────────────────────
PlanOption = Literal["basic", "pro", "enterprise"]
RoleOption = Literal["owner", "reseller", "client"]
StatusOption = Literal["active", "inactive", "deleted", "suspended"]
SubscriptionStatusOption = Literal["trial", "active", "past_due", "canceled", "inactive"]

# ── Data shape (DB row) ────────────────────────────────────
class ClientProfile(BaseModel):
    """
    Complete client profile from database.
    NO password_hash for security.
    """
    id: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    company: Optional[str] = None
    plan: PlanOption
    role: RoleOption
    status: StatusOption
    subscription_status: SubscriptionStatusOption
    trial_active: bool
    trial_ends_at: Optional[datetime] = None
    reseller_id: Optional[str] = None
    avatar_url: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ── Create payload ─────────────────────────────────────────
class ClientCreate(BaseModel):
    """Request payload for creating new client"""
    email: EmailStr = Field(..., description="Client email (unique)")
    name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=50)
    company: Optional[str] = Field(default=None, max_length=200)
    plan: PlanOption = "basic"
    notes: Optional[str] = Field(default=None, max_length=2000)
    reseller_id: Optional[str] = Field(
        default=None,
        description="Reseller UUID (auto-assigned if creator is reseller)"
    )

# ── Update payload (all Optional) ──────────────────────────
class ClientUpdate(BaseModel):
    """Request payload for updating existing client"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    company: Optional[str] = Field(default=None, max_length=200)
    plan: Optional[PlanOption] = None
    notes: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[StatusOption] = None
    subscription_status: Optional[SubscriptionStatusOption] = None
    trial_active: Optional[bool] = None
    trial_ends_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None

# ── Response envelopes ─────────────────────────────────────
class ClientResponse(BaseModel):
    """Standard API response for single client operations"""
    success: bool
    data: Optional[ClientProfile] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ClientListResponse(BaseModel):
    """API response for list operations"""
    success: bool
    data: List[ClientProfile] = Field(default_factory=list)
    total: int = 0
    message: Optional[str] = None
    error: Optional[str] = None

# ── Home dashboard payload ─────────────────────────────────
class ClientHomeStats(BaseModel):
    """Stats for client home dashboard"""
    total_posts: int = 0
    connected_accounts: int = 0
    this_month_posts: int = 0

class ClientHomeData(BaseModel):
    """Complete client home dashboard data"""
    profile: ClientProfile
    social_accounts: List[dict] = Field(default_factory=list)
    upcoming_posts: List[dict] = Field(default_factory=list)
    stats: ClientHomeStats

class ClientHomeResponse(BaseModel):
    """API response for client home endpoint"""
    success: bool
    data: Optional[ClientHomeData] = None
    message: Optional[str] = None
    error: Optional[str] = None
