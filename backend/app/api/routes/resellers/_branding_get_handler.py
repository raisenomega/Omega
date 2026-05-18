"""Handler: GET reseller branding with defaults and sanitization"""
import logging
from app.models.reseller_models import sanitize_json_field

logger = logging.getLogger(__name__)

_DEFAULT_BRANDING_FIELDS = {
    "primary_color": "38 85% 55%",
    "secondary_color": "225 12% 14%",
    "hero_cta_text": "Comenzar",
    "agency_name": None,
    "logo_url": None,
    "hero_type": None,
    "hero_media_url": None,
    "hero_title": None,
    "hero_subtitle": None,
    "hero_cta_url": None,
    "pain_section": {},
    "solutions_section": {},
    "services_section": {},
    "metrics_section": {},
    "process_section": {},
    "testimonials_section": {},
    "client_logos_section": {},
    "contact_email": None,
    "contact_phone": None,
    "footer_text": None,
    "social_links": {},
    "pricing_plans": [],
}

_JSONB_FIELDS = [
    "pain_section", "solutions_section", "services_section",
    "metrics_section", "process_section", "testimonials_section",
    "client_logos_section", "social_links",
]


async def handle_get_branding(service, reseller_id: str) -> dict:
    """Retrieve branding config. Returns defaults if not yet configured."""
    try:
        reseller_response = service.client.table("resellers")\
            .select("slug")\
            .eq("id", reseller_id)\
            .execute()
        slug = reseller_response.data[0].get("slug") if reseller_response.data else None
    except Exception as e:
        logger.warning(f"Could not fetch slug for reseller {reseller_id}: {e}")
        slug = None

    branding = await service.get_branding(reseller_id)

    if not branding:
        return {"reseller_id": reseller_id, "slug": slug, **_DEFAULT_BRANDING_FIELDS}

    branding["slug"] = slug

    for field in _JSONB_FIELDS:
        branding[field] = sanitize_json_field(branding.get(field))

    branding["pricing_plans"] = branding.get("pricing_plans") or []

    return branding
