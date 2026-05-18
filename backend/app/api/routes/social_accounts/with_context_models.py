"""Models for Social Account With Context endpoints"""
from pydantic import BaseModel, Field
from typing import Optional, List
from app.api.routes.social_accounts.models import PlatformOption

PLAN_LIMITS = {"basic": 2, "pro": 5, "enterprise": float('inf')}


class ContextData(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=200)
    industry: str = Field(..., min_length=1, max_length=100)
    business_description: Optional[str] = Field(default=None, max_length=1000)
    communication_tone: str = Field(default="casual")
    primary_goal: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    forbidden_words: List[str] = Field(default_factory=list)
    forbidden_topics: List[str] = Field(default_factory=list)
    brand_colors: List[str] = Field(default_factory=list)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    website_url: Optional[str] = Field(default=None, max_length=500)
    custom_instructions: Optional[str] = None


class SocialAccountWithContextCreate(BaseModel):
    client_id: str = Field(..., description="Client UUID")
    platform: PlatformOption
    username: str = Field(..., min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context: ContextData


class SocialAccountWithContextUpdate(BaseModel):
    username: Optional[str] = Field(default=None, min_length=1, max_length=255)
    profile_url: Optional[str] = Field(default=None, max_length=500)
    context: Optional[ContextData] = None
