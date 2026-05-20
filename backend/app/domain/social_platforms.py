"""Canonical social platforms · metadata para OAuth Fase 2 (DEBT-040).

Cero imports externos (DDD A2). Cada plataforma declara sus requisitos
de integración para que el wizard capture el shape correcto desde día 1.
"""
from typing import Final
from types import MappingProxyType

PLATFORMS: Final[frozenset[str]] = frozenset({
    "instagram", "facebook", "tiktok", "twitter", "linkedin", "youtube",
})


# requires_fb_page: Instagram Business requiere FB Page asociada (Meta API).
# oauth_scopes: shape preliminar · Fase 2 ajusta contra Developer App real.
# supports_auto_publish: True solo en plataformas con API write confirmada.
PLATFORM_METADATA: Final = MappingProxyType({
    "instagram": MappingProxyType({
        "label": "Instagram",
        "requires_fb_page": True,
        "oauth_scopes": ("instagram_basic", "instagram_content_publish", "pages_show_list"),
        "supports_auto_publish": True,
        "supports_business_account": True,
    }),
    "facebook": MappingProxyType({
        "label": "Facebook",
        "requires_fb_page": False,
        "oauth_scopes": ("pages_show_list", "pages_manage_posts", "pages_read_engagement"),
        "supports_auto_publish": True,
        "supports_business_account": True,
    }),
    "tiktok": MappingProxyType({
        "label": "TikTok",
        "requires_fb_page": False,
        "oauth_scopes": ("user.info.basic", "video.publish", "video.upload"),
        "supports_auto_publish": True,
        "supports_business_account": True,
    }),
    "twitter": MappingProxyType({
        "label": "X (Twitter)",
        "requires_fb_page": False,
        "oauth_scopes": ("tweet.read", "tweet.write", "users.read"),
        "supports_auto_publish": True,
        "supports_business_account": False,
    }),
    "linkedin": MappingProxyType({
        "label": "LinkedIn",
        "requires_fb_page": False,
        "oauth_scopes": ("w_member_social", "r_liteprofile"),
        "supports_auto_publish": True,
        "supports_business_account": True,
    }),
    "youtube": MappingProxyType({
        "label": "YouTube",
        "requires_fb_page": False,
        "oauth_scopes": ("https://www.googleapis.com/auth/youtube.upload",),
        "supports_auto_publish": True,
        "supports_business_account": True,
    }),
})
