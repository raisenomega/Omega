"""Helpers puros del onboarding · validación + completion percent (A5)."""
from typing import Optional, Tuple
from app.domain.client_constants import (
    INDUSTRIES, REGIONS, BUSINESS_SIZES, TONES, EMOJI_USAGE,
    HASHTAG_STRATEGY, PRIMARY_GOALS,
    GENDERS, CONTENT_FORMATS, PUBLISHING_FREQUENCIES,
)
from app.domain.social_platforms import PLATFORMS
from app.api.routes.clients_v3.models.onboarding import OnboardingPayload


def validate_payload(p: OnboardingPayload) -> Tuple[bool, Optional[str]]:
    """Result-tuple (A5): (ok, error_code) · valida enums dominio."""
    if p.identity.industry not in INDUSTRIES:
        return (False, "invalid_industry")
    if not p.identity.regions:
        return (False, "empty_regions")
    for r in p.identity.regions:
        if r not in REGIONS:
            return (False, f"invalid_region:{r}")
    if p.business.business_size is not None and p.business.business_size not in BUSINESS_SIZES:
        return (False, "invalid_business_size")
    for t in p.brand_voice.tone:
        if t not in TONES:
            return (False, f"invalid_tone:{t}")
    if p.brand_voice.emoji_usage is not None and p.brand_voice.emoji_usage not in EMOJI_USAGE:
        return (False, "invalid_emoji_usage")
    if p.brand_voice.hashtag_strategy is not None and p.brand_voice.hashtag_strategy not in HASHTAG_STRATEGY:
        return (False, "invalid_hashtag_strategy")
    if len(p.goals.primary_goal) > 3:
        return (False, "too_many_primary_goals")
    for g in p.goals.primary_goal:
        if g not in PRIMARY_GOALS:
            return (False, f"invalid_primary_goal:{g}")
    if p.audience.audience_gender is not None and p.audience.audience_gender not in GENDERS:
        return (False, "invalid_gender")
    for fmt in p.brand_voice.preferred_formats:
        if fmt not in CONTENT_FORMATS:
            return (False, f"invalid_format:{fmt}")
    for acc in p.social_accounts:
        if acc.platform not in PLATFORMS:
            return (False, f"invalid_platform:{acc.platform}")
        if acc.publishing_frequency is not None and acc.publishing_frequency not in PUBLISHING_FREQUENCIES:
            return (False, "invalid_publishing_frequency")
    primary_count = sum(1 for a in p.social_accounts if a.is_primary)
    if primary_count > 1:
        return (False, "multiple_primary_accounts")
    return (True, None)


def calc_completion_percent(p: OnboardingPayload) -> int:
    """% de las 10 secciones con al menos 1 campo no-vacío · 0-100."""
    filled = 0
    if p.identity.name and p.identity.industry and p.identity.regions:
        filled += 1
    if any([p.business.niche, p.business.business_what, p.business.business_to_whom, p.business.business_diff]):
        filled += 1
    if any([p.audience.target_audience, p.audience.audience_age_range, p.audience.competitors]):
        filled += 1
    if any([p.brand_voice.tone, p.brand_voice.brand_voice_keywords, p.brand_voice.preferred_formats]):
        filled += 1
    if any([p.goals.primary_goal, p.goals.goal_this_month, p.goals.success_metric]):
        filled += 1
    if any([p.content_history.has_existing_content, p.content_history.best_post_url, p.content_history.what_worked]):
        filled += 1
    if p.social_accounts:
        filled += 1
    if any([p.instructions.custom_instructions, p.instructions.emergency_contact_name, p.instructions.preferred_publishing_hours]):
        filled += 1
    if p.brand_assets is not None and any([p.brand_assets.primary_color, p.brand_assets.logo_file_id]):
        filled += 1
    if p.brand_voice_samples:
        filled += 1
    return int((filled / 10) * 100)
