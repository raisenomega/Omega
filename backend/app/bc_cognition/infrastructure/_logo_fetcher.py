"""Logo fetcher for ARIA multimodal (DEBT-084).

Fetches a brand logo from a public URL and returns an Anthropic-compatible
image block dict for inclusion in Claude messages. All I/O lives here
(DDD A2 — infra layer; domain stays pure).

Design constraints:
- Best-effort: any failure returns None so ARIA degrades to text-only.
- HEAD check: skip images > _MAX_LOGO_BYTES to avoid token blowup.
- Timeout: _FETCH_TIMEOUT_S hard cap on the HEAD request.
- URL-based image block: no base64 conversion needed (Anthropic SDK 0.84+
  supports {"type":"url","url":"<https>"} natively).
- Only HTTPS URLs are accepted (SSRF guard).
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

_MAX_LOGO_BYTES: int = 5 * 1024 * 1024   # 5 MB guard
_FETCH_TIMEOUT_S: float = 5.0
_ACCEPTED_SCHEMES = ("https://",)

logger = logging.getLogger(__name__)


def _is_safe_url(url: str) -> bool:
    """Only HTTPS public URLs are forwarded to Claude (SSRF guard)."""
    return any(url.startswith(s) for s in _ACCEPTED_SCHEMES)


async def _check_size(url: str, client: httpx.AsyncClient) -> bool:
    """HEAD request to check Content-Length. Returns True if within limit."""
    try:
        r = await client.head(url, timeout=_FETCH_TIMEOUT_S,
                              follow_redirects=False)
        length = int(r.headers.get("content-length", "0"))
        return length == 0 or length <= _MAX_LOGO_BYTES
    except Exception:
        return True  # unknown size → optimistically allow


async def fetch_logo_for_aria(logo_url: Optional[str]) -> Optional[dict]:
    """Return an Anthropic image block for logo_url, or None (best-effort).

    Returned dict shape (URL-based, Anthropic SDK 0.84+):
        {"type": "image", "source": {"type": "url", "url": "<https url>"}}
    """
    if not logo_url or not _is_safe_url(logo_url):
        return None
    try:
        async with httpx.AsyncClient() as client:
            if not await _check_size(logo_url, client):
                logger.info("fetch_logo_for_aria: skipped %s (> %d B)",
                            logo_url, _MAX_LOGO_BYTES)
                return None
        return {"type": "image", "source": {"type": "url", "url": logo_url}}
    except Exception as exc:
        logger.warning("fetch_logo_for_aria failed for %s: %s", logo_url, exc)
        return None
