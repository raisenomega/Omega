"""Use case · GET /brand-voice/summary · read-only · Sprint 2 ②.A.

Orquesta 3 lecturas del repo brand_voice_corpus_repository y agrega top
keywords desde tone_tags. DDD A1/A9: handler -> use_case -> repo (cero
acceso Supabase directo aquí). Best-effort: si el repo retorna [], la
respuesta es válida con conteos = 0 y listas vacías.
"""
from collections import Counter

from app.bc_cognition.infrastructure.brand_voice_corpus_repository import (
    count_corpus, fetch_recent_corpus, fetch_tone_tags_only,
)

_LATEST_LIMIT = 5
_KEYWORDS_LIMIT = 10
_TONE_SAMPLE = 200


def build_brand_voice_summary(client_id: str) -> dict:
    """Retorna dict con corpus_count, latest_approvals, top_keywords."""
    count = count_corpus(client_id)
    latest = fetch_recent_corpus(client_id, limit=_LATEST_LIMIT)
    tag_lists = fetch_tone_tags_only(client_id, limit=_TONE_SAMPLE)

    return {
        "corpus_count": count,
        "latest_approvals": [_to_entry(r) for r in latest],
        "top_keywords": _aggregate_keywords(tag_lists, _KEYWORDS_LIMIT),
    }


def _to_entry(row: dict) -> dict:
    return {
        "text": row.get("text") or "",
        "platform": row.get("platform"),
        "created_at": str(row.get("created_at") or ""),
    }


def _aggregate_keywords(tag_lists: list[list[str]], top_n: int) -> list[dict]:
    """Flatten todas las tone_tags + Counter + top-N (excluye strings vacíos)."""
    flat = [t.strip().lower() for tags in tag_lists for t in tags if t and t.strip()]
    if not flat:
        return []
    return [
        {"keyword": kw, "count": cnt}
        for kw, cnt in Counter(flat).most_common(top_n)
    ]
