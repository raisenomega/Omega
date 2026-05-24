"""Builder pure function · transforma corpus rows → BrandDNA.

No I/O · no estado · solo lectura del input. Testeable directamente.
Spec: CONTENT_LAB_OMEGA_MASTER.md §6 (Brand DNA Engine).
"""
import re
from collections import Counter
from datetime import datetime
from typing import Optional

from app.bc_cognition.application._brand_dna_scoring import compute_score
from app.bc_cognition.application._brand_dna_stopwords import STOPWORDS
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.domain.industry_defaults import get_defaults


_WORD_RE = re.compile(r"\w+", re.UNICODE)
_TOP_KEYWORDS = 10
_TOP_TONES = 5
_TOP_POSTS = 3
_POST_EXCERPT_WORDS = 150


def build_brand_dna(
    corpus: list[dict],
    now: Optional[datetime] = None,
    vertical: Optional[str] = None,
) -> BrandDNA:
    if not corpus:
        # DEBT-CL-019: fallback a industry defaults si vertical conocido.
        # score=0 + corpus_size=0 signal claro: NO es data real del cliente.
        defaults = get_defaults(vertical)
        if defaults:
            return BrandDNA(
                tone=list(defaults["tone"]),
                keywords=[(kw, 0) for kw in defaults["keywords"]],
                avg_length_words=0,
                top_post_excerpts=[],
                corpus_size=0,
                score=0.0,
            )
        return BrandDNA.empty()

    now = now or datetime.utcnow()

    tone_counter: Counter[str] = Counter()
    for row in corpus:
        for tag in row.get("tone_tags") or []:
            tone_counter[tag] += 1
    tone = [t for t, _ in tone_counter.most_common(_TOP_TONES)]

    keyword_counter: Counter[str] = Counter()
    total_words = 0
    for row in corpus:
        words = _WORD_RE.findall((row.get("text") or "").lower())
        total_words += len(words)
        for w in words:
            if len(w) >= 3 and w not in STOPWORDS:
                keyword_counter[w] += 1
    keywords = keyword_counter.most_common(_TOP_KEYWORDS)

    avg_length_words = total_words // len(corpus)

    ranked = sorted(corpus, key=lambda r: r.get("engagement_score") or 0, reverse=True)
    top_post_excerpts = [
        _truncate_words(r.get("text") or "", _POST_EXCERPT_WORDS)
        for r in ranked[:_TOP_POSTS]
    ]

    return BrandDNA(
        tone=tone,
        keywords=keywords,
        avg_length_words=avg_length_words,
        top_post_excerpts=top_post_excerpts,
        corpus_size=len(corpus),
        score=compute_score(corpus, now),
    )


def _truncate_words(text: str, n: int) -> str:
    words = text.split()
    if len(words) <= n:
        return text
    return " ".join(words[:n]) + "…"
