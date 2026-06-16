"""Pure scoring function for BrandDNA · no I/O.

Fórmula: weighted sum de 4 componentes (corpus_size, recency, diversity,
quality). Gate N<3 fuerza weak para corpus mínimo viable.
"""
from datetime import datetime, timedelta, timezone


_WEIGHTS = {
    "corpus_size": 0.30,
    "recency": 0.20,
    "diversity": 0.20,
    "quality": 0.30,
}

_SOURCE_QUALITY_WEIGHT = {
    "approved_draft": 1.0,
    "top_performing_post": 1.0,
    "manual_upload": 0.5,
}


def compute_score(corpus: list[dict], now: datetime) -> float:
    n = len(corpus)
    if n == 0:
        return 0.0

    corpus_size_score = min(n / 20.0, 1.0)

    # aware-safe: naive `now` (p.ej. caller legacy o tests) se trata como UTC ·
    # _to_datetime también devuelve aware → la comparación nunca mezcla naive/aware.
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    thirty_days_ago = now - timedelta(days=30)
    posts_30d = sum(
        1 for p in corpus
        if _to_datetime(p.get("created_at")) >= thirty_days_ago
    )
    recency_score = min(posts_30d / 10.0, 1.0)

    unique_tones = {
        t for p in corpus for t in (p.get("tone_tags") or [])
    }
    diversity_score = min(len(unique_tones) / 5.0, 1.0)

    quality_total = sum(
        _SOURCE_QUALITY_WEIGHT.get(p.get("source") or "", 0.0) for p in corpus
    )
    quality_score = quality_total / n

    score = (
        corpus_size_score * _WEIGHTS["corpus_size"]
        + recency_score * _WEIGHTS["recency"]
        + diversity_score * _WEIGHTS["diversity"]
        + quality_score * _WEIGHTS["quality"]
    )

    if n < 3:
        return min(score, 0.29)
    return round(score, 4)


def _to_datetime(value) -> datetime:
    """Normaliza a datetime aware-UTC (naive → se asume UTC). Mantiene toda
    comparación en aware vs aware (Supabase devuelve aware)."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)
    return datetime.min.replace(tzinfo=timezone.utc)
