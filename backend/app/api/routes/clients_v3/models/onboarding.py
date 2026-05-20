"""POST /clients/onboarding · request + response models (Wizard V3)."""
from pydantic import BaseModel, Field
from app.api.routes.clients_v3.models.onboarding_sections import (
    IdentitySection, BusinessSection, AudienceSection,
    BrandVoiceSection, GoalsSection, ContentHistorySection,
)
from app.api.routes.clients_v3.models.onboarding_extra import (
    SocialAccountInput, SpecialInstructionsSection, BrandAssetsSection,
)


class OnboardingPayload(BaseModel):
    identity: IdentitySection
    business: BusinessSection = Field(default_factory=BusinessSection)
    audience: AudienceSection = Field(default_factory=AudienceSection)
    brand_voice: BrandVoiceSection = Field(default_factory=BrandVoiceSection)
    goals: GoalsSection = Field(default_factory=GoalsSection)
    content_history: ContentHistorySection = Field(default_factory=ContentHistorySection)
    social_accounts: list[SocialAccountInput] = Field(default_factory=list)
    instructions: SpecialInstructionsSection = Field(default_factory=SpecialInstructionsSection)
    brand_assets: BrandAssetsSection | None = None
    brand_voice_samples: list[str] = Field(default_factory=list)


class OnboardingResponse(BaseModel):
    client_id: str
    completion_percent: int
    onboarding_complete: bool
