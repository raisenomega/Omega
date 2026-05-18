"""
Context Domain Models
Pydantic schemas for client context management.
Zero business logic. Zero infrastructure imports.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime

# ── Literal types ──────────────────────────────────────────
ToneOption = Literal[
    "professional", "casual", "inspirational",
    "educational", "humorous", "energetic"
]

GoalOption = Literal[
    "sales", "awareness", "community", "leads", "retention"
]

PlatformOption = Literal[
    "instagram", "tiktok", "facebook", "linkedin", "twitter"
]

# ── Data shape (DB row) ────────────────────────────────────
class ClientContextData(BaseModel):
    """Complete client context profile from database"""
    id: str
    client_id: str
    version: int
    business_name: str
    industry: str
    business_description: Optional[str] = None
    # target_audience structure varies by industry (age, location, interests, etc.)
    target_audience: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audience demographics (flexible schema)"
    )
    communication_tone: ToneOption = "casual"
    primary_goal: Optional[GoalOption] = None
    platforms: List[PlatformOption] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=list)
    forbidden_topics: List[str] = Field(default_factory=list)
    brand_colors: List[str] = Field(default_factory=list)
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    ai_generated_brief: Optional[str] = None
    custom_instructions: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

# ── Create payload ─────────────────────────────────────────
class ClientContextCreate(BaseModel):
    """Request payload for creating new client context"""
    client_id: str = Field(..., description="UUID del cliente")
    business_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    business_description: Optional[str] = Field(
        default=None, max_length=1000
    )
    # target_audience structure varies by industry
    target_audience: Dict[str, Any] = Field(
        default_factory=dict,
        description="Audience demographics (flexible schema)"
    )
    communication_tone: ToneOption = "casual"
    primary_goal: Optional[GoalOption] = None
    platforms: List[PlatformOption] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=list)
    forbidden_topics: List[str] = Field(default_factory=list)
    brand_colors: List[str] = Field(default_factory=list)
    website_url: Optional[str] = None
    custom_instructions: Optional[str] = None

# ── Update payload (todos Optional) ───────────────────────
class ClientContextUpdate(BaseModel):
    """Request payload for updating existing client context"""
    business_name: Optional[str] = Field(
        default=None, min_length=1, max_length=200
    )
    industry: Optional[str] = Field(
        default=None, min_length=1, max_length=100
    )
    business_description: Optional[str] = Field(
        default=None, max_length=1000
    )
    # target_audience structure varies by industry
    target_audience: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Audience demographics (flexible schema)"
    )
    communication_tone: Optional[ToneOption] = None
    primary_goal: Optional[GoalOption] = None
    platforms: Optional[List[PlatformOption]] = None
    keywords: Optional[List[str]] = None
    forbidden_words: Optional[List[str]] = None
    forbidden_topics: Optional[List[str]] = None
    brand_colors: Optional[List[str]] = None
    website_url: Optional[str] = None
    custom_instructions: Optional[str] = None
    ai_generated_brief: Optional[str] = None

# ── Response envelope ──────────────────────────────────────
class ClientContextResponse(BaseModel):
    """Standard API response for context operations"""
    success: bool
    data: Optional[ClientContextData] = None
    error: Optional[str] = None
    message: Optional[str] = None
