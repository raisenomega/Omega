"""Transform DB rows -> OnboardingPayload shape · usado por GET /onboarding-data.

CSV split para region/tone/primary_goal (almacenados como text CSV en DB ·
ver DEBT-042). Sin Any · solo str|list|dict.
"""
from typing import Any, Optional


def _csv_split(s: Optional[str]) -> list[str]:
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def _pick(row: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {k: row.get(k) for k in keys}


BUSINESS_K = ("niche", "vertical", "business_what", "business_to_whom", "business_diff", "business_size", "years_operating")
AUDIENCE_K = ("target_audience", "audience_age_range", "audience_gender")
BRAND_VOICE_K = ("avoided_topics", "avoided_words", "preferred_formats", "emoji_usage", "hashtag_strategy")
GOALS_K = ("goal_this_month", "goal_this_quarter", "goal_priority_now", "success_metric", "monthly_revenue_target")
HISTORY_K = ("has_existing_content", "existing_followers", "best_post_url", "what_worked", "what_failed", "content_themes")
INSTR_K = ("custom_instructions", "emergency_contact_name", "emergency_contact_phone", "requires_publish_approval", "preferred_publishing_hours", "timezone")
ASSETS_K = ("primary_color", "secondary_color", "accent_color", "font_primary", "font_secondary", "logo_file_id", "brand_guide_file_id")
SOCIAL_K = ("platform", "username", "profile_url", "is_primary", "auto_publish_allowed", "approx_followers", "publishing_frequency", "is_business_account")


def to_onboarding_payload(
    client: dict[str, Any],
    context: dict[str, Any],
    accounts: list[dict[str, Any]],
    assets: dict[str, Any],
    samples: Optional[list[str]] = None,
) -> dict[str, Any]:
    bv_obj = context.get("brand_voice")
    bv_keywords = bv_obj.get("keywords", []) if isinstance(bv_obj, dict) else []
    return {
        "identity": {
            "name": client.get("name") or "",
            "industry": client.get("industry") or "",
            "regions": _csv_split(client.get("region")),
        },
        "business": _pick(context, BUSINESS_K),
        "audience": {**_pick(context, AUDIENCE_K), "competitors": context.get("competitors") or []},
        "brand_voice": {"tone": _csv_split(context.get("tone")), "brand_voice_keywords": bv_keywords, **_pick(context, BRAND_VOICE_K)},
        "goals": {"primary_goal": _csv_split(context.get("primary_goal")), **_pick(context, GOALS_K)},
        "content_history": _pick(context, HISTORY_K),
        "social_accounts": [{k: a.get(k) for k in SOCIAL_K} for a in accounts],
        "instructions": _pick(context, INSTR_K),
        "brand_assets": _pick(assets, ASSETS_K) if assets else None,
        "brand_voice_samples": samples or [],
    }
