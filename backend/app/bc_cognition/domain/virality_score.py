"""Virality Score V1 · pure heuristic 0-100 · CONTENT_LAB §9.2 · Sprint 2 P3.

Sin Meta API · badge 'Estimado' obligatorio (P1). Features (suma 100):
hook 20 + CTA 25 + question 15 + emojis 15 + length 25. Length compara vs
dna.avg_length_words si corpus_size>=5 · else _PLATFORM_DEFAULT_WORDS.
"""
import re
from typing import Final

from app.bc_cognition.domain.brand_dna import BrandDNA


_EMOJI_RE: Final = re.compile(
    r"[\U0001F000-\U0001FFFF\U00002600-\U000027FF\U0001FA00-\U0001FA9F]"
)
_CTA_VERBS_STRONG: Final[frozenset[str]] = frozenset({
    "agenda", "reserva", "reservá", "descarga", "descargá", "compra", "comprá",
    "escríbenos", "escribime", "comentá", "comenta", "guardá", "guarda",
    "shop", "buy", "download", "subscribe", "comment", "click", "tap", "swipe",
})
_PLATFORM_DEFAULT_WORDS: Final[dict[str, int]] = {
    "instagram": 130, "facebook": 110, "tiktok": 40, "linkedin": 400,
    "twitter": 30, "google_business": 100, "email": 200,
}
_DNA_STRONG_THRESHOLD: Final = 5


def compute_virality_score(text: str, dna: BrandDNA, platform: str) -> dict:
    """Retorna {score: 0-100, breakdown: {...}, estimated: True}."""
    text = text or ""
    words = text.split()
    target = (
        dna.avg_length_words if dna.corpus_size >= _DNA_STRONG_THRESHOLD
        else _PLATFORM_DEFAULT_WORDS.get(platform, 130)
    )
    breakdown = {
        "hook": _hook_score(words),
        "cta": _cta_score(text),
        "question": 15 if "?" in text else 0,
        "emojis": _emoji_score(text),
        "length": _length_score(len(words), target),
    }
    return {"score": sum(breakdown.values()), "breakdown": breakdown, "estimated": True}


def _hook_score(words: list[str]) -> int:
    if not words:
        return 0
    first = words[0]
    if first[0] in "¿\"'0123456789" or _EMOJI_RE.match(first):
        return 20
    return 10 if len(first) <= 8 else 5


def _cta_score(text: str) -> int:
    tail = " ".join(text.split()[-25:]).lower()
    if any(v in tail for v in _CTA_VERBS_STRONG):
        return 25
    return 12 if ("contact" in tail or "contáct" in tail) else 0


def _emoji_score(text: str) -> int:
    n = len(_EMOJI_RE.findall(text))
    if 1 <= n <= 3:
        return 15
    return 8 if 4 <= n <= 6 else 0


def _length_score(actual: int, target: int) -> int:
    if target <= 0:
        return 0
    ratio = abs(actual - target) / target
    if ratio <= 0.3:
        return 25
    return 12 if ratio <= 0.6 else 0
