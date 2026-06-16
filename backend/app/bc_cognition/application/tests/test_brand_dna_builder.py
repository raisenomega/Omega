"""Tests pure logic of brand_dna_builder (no I/O · solo fixtures).

Located in application/tests/ porque bc_cognition/domain/tests/ no existe
todavía. El builder es pure function · este test verifica:
  - corpus vacío → BrandDNA.empty
  - N<3 → gate fuerza score ≤ 0.29 (weak)
  - mixed sources + parcial recency → emerging
  - 20 approved + diverso + reciente → strong
"""
from datetime import datetime, timedelta, timezone

from app.bc_cognition.application._brand_dna_builder import build_brand_dna
from app.bc_cognition.domain.brand_dna import BrandDNA


_NOW = datetime(2026, 5, 21, 12, 0, 0)
_RECENT = (_NOW - timedelta(days=5)).isoformat()
_OLD = (_NOW - timedelta(days=200)).isoformat()


def _post(text="hola mundo casero fresco familia tradición sabor",
          tone=None, source="approved_draft", engagement=1.0, created_at=None) -> dict:
    return {
        "id": "id1", "text": text, "tone_tags": tone or ["casero"],
        "platform": "instagram", "engagement_score": engagement,
        "source": source, "created_at": created_at or _RECENT,
    }


def test_empty_corpus_returns_weak_default() -> None:
    dna = build_brand_dna([], now=_NOW)
    assert dna == BrandDNA.empty()
    assert dna.confidence_label() == "weak"
    assert dna.is_weak() and not dna.is_strong()


def test_n_one_approved_capped_to_weak() -> None:
    dna = build_brand_dna([_post()], now=_NOW)
    assert dna.corpus_size == 1
    assert dna.score <= 0.29
    assert dna.confidence_label() == "weak"


def test_emerging_with_mixed_sources() -> None:
    corpus = (
        [_post(tone=["casero"], source="approved_draft", created_at=_RECENT) for _ in range(3)]
        + [_post(tone=["fresco"], source="manual_upload", created_at=_OLD) for _ in range(4)]
        + [_post(tone=["familiar"], source="top_performing_post", created_at=_OLD) for _ in range(3)]
    )
    dna = build_brand_dna(corpus, now=_NOW)
    assert dna.corpus_size == 10
    assert 0.3 <= dna.score < 0.7
    assert dna.confidence_label() == "emerging"


def test_aware_now_does_not_raise_naive_vs_aware() -> None:
    """P2 P8a regresión: el default de producción es `datetime.now(timezone.utc)`
    (aware). Antes de hardenar _to_datetime, comparar el created_at (parseado
    aware) contra un thirty_days_ago naive lanzaba TypeError. Con now aware el
    score debe computarse sin error y reflejar la recencia."""
    aware_now = datetime(2026, 5, 21, 12, 0, 0, tzinfo=timezone.utc)
    recent = (aware_now - timedelta(days=5)).isoformat()  # ISO con +00:00
    corpus = [_post(tone=["casero"], source="approved_draft", created_at=recent)
              for _ in range(3)]
    dna = build_brand_dna(corpus, now=aware_now)
    assert dna.corpus_size == 3
    assert dna.score >= 0.0


def test_strong_with_full_approved_corpus() -> None:
    tones = ["casero", "fresco", "familiar", "tradicional", "cálido"]
    corpus = [
        _post(tone=[tones[i % 5]], source="approved_draft", engagement=5.0,
              created_at=_RECENT)
        for i in range(20)
    ]
    dna = build_brand_dna(corpus, now=_NOW)
    assert dna.corpus_size == 20
    assert dna.score >= 0.7
    assert dna.confidence_label() == "strong"
    assert dna.is_strong()
    assert len(dna.top_post_excerpts) == 3
    assert len(dna.tone) == 5
    assert all(len(w) >= 3 for w, _ in dna.keywords)
