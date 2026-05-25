"""Pydantic sub-models · secciones 7-9 del Wizard V3 (multi-row + optional)."""
from typing import Optional
from pydantic import BaseModel, Field


class SocialAccountInput(BaseModel):
    platform: str
    username: str = Field(..., min_length=1, max_length=500)  # tolera URLs largas · se mapea a account_name
    profile_url: Optional[str] = None
    is_primary: bool = False
    auto_publish_allowed: bool = False
    approx_followers: Optional[int] = Field(default=None, ge=0)
    publishing_frequency: Optional[str] = None
    is_business_account: bool = False


class SpecialInstructionsSection(BaseModel):
    custom_instructions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    requires_publish_approval: bool = True
    preferred_publishing_hours: list[int] = Field(default_factory=list)
    timezone: str = "America/Puerto_Rico"


class BrandAssetsSection(BaseModel):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_primary: Optional[str] = None
    font_secondary: Optional[str] = None
    logo_file_id: Optional[str] = None
    brand_guide_file_id: Optional[str] = None
