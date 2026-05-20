"""Pydantic sub-models · secciones 1-6 del Wizard V3."""
from typing import Optional
from pydantic import BaseModel, Field


class IdentitySection(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    industry: str = Field(..., max_length=64)
    region: str = Field(..., max_length=64)


class BusinessSection(BaseModel):
    niche: Optional[str] = None
    vertical: Optional[str] = None
    business_what: Optional[str] = None
    business_to_whom: Optional[str] = None
    business_diff: Optional[str] = None
    business_size: Optional[str] = None
    years_operating: Optional[int] = Field(default=None, ge=0)


class AudienceSection(BaseModel):
    target_audience: Optional[str] = None
    audience_age_range: Optional[str] = None
    audience_gender: Optional[str] = None
    competitors: list[dict] = Field(default_factory=list)


class BrandVoiceSection(BaseModel):
    tone: Optional[str] = None
    brand_voice_keywords: list[str] = Field(default_factory=list)
    avoided_topics: Optional[str] = None
    avoided_words: list[str] = Field(default_factory=list)
    preferred_formats: list[str] = Field(default_factory=list)
    emoji_usage: Optional[str] = None
    hashtag_strategy: Optional[str] = None


class GoalsSection(BaseModel):
    primary_goal: Optional[str] = None
    goal_this_month: Optional[str] = None
    goal_this_quarter: Optional[str] = None
    goal_priority_now: Optional[str] = None
    success_metric: Optional[str] = None
    monthly_revenue_target: Optional[float] = Field(default=None, ge=0)


class ContentHistorySection(BaseModel):
    has_existing_content: bool = False
    existing_followers: Optional[int] = Field(default=None, ge=0)
    best_post_url: Optional[str] = None
    what_worked: Optional[str] = None
    what_failed: Optional[str] = None
    content_themes: list[str] = Field(default_factory=list)
