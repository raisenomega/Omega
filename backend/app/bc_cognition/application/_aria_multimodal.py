"""ARIA multimodal content builder (DEBT-084).

Thin application-layer bridge: takes the user message text and an optional
logo URL, calls the infrastructure fetcher, and returns a Claude-ready
content value (str when no image, list-of-blocks when image is available).

Domain purity (A2): zero external I/O here — all network work is delegated
to _logo_fetcher in the infrastructure layer.
"""
from __future__ import annotations

from typing import Optional, Union

from app.bc_cognition.infrastructure._logo_fetcher import fetch_logo_for_aria


async def build_user_content(
    user_message: str,
    logo_url: Optional[str],
) -> Union[str, list]:
    """Return Claude-ready content for the user turn.

    - No logo  →  plain str (existing behaviour, zero regression).
    - Logo URL →  [image_block, text_block] so Claude sees the brand logo.

    Always best-effort: if the logo fetch fails, falls back to plain str.
    """
    logo_block = await fetch_logo_for_aria(logo_url)
    if logo_block is None:
        return user_message
    return [
        logo_block,
        {"type": "text", "text": user_message},
    ]
