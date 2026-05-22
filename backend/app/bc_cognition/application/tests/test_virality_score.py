"""Tests para virality_score · pure heuristic (no I/O · no fixtures DB).

Mismo patrón que test_brand_dna_builder / test_aria_memory_context.
"""
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.domain.virality_score import compute_virality_score


def _dna(corpus_size: int = 0, avg_length: int = 130) -> BrandDNA:
    return BrandDNA(
        tone=[], keywords=[], avg_length_words=avg_length,
        top_post_excerpts=[], corpus_size=corpus_size, score=0.0,
    )


def test_empty_text_returns_zero() -> None:
    r = compute_virality_score("", _dna(), "instagram")
    assert r["score"] == 0
    assert all(v == 0 for v in r["breakdown"].values())
    assert r["estimated"] is True


def test_perfect_caption_high_score() -> None:
    # 130 palabras aprox · hook número · CTA strong · question · 2 emojis
    body = "casero fresco familia tradición " * 30
    text = f"3 razones para visitarnos hoy 🔥 {body}🌟 ¿probás? Reservá ahora"
    r = compute_virality_score(text, _dna(corpus_size=10, avg_length=130), "instagram")
    assert r["score"] >= 80, f"expected >=80, got {r['score']} · {r['breakdown']}"
    assert r["breakdown"]["question"] == 15
    assert r["breakdown"]["emojis"] == 15
    assert r["breakdown"]["cta"] == 25


def test_too_long_no_cta_low_score() -> None:
    text = "lorem ipsum dolor sit amet " * 200  # ~1000 palabras · target 130
    r = compute_virality_score(text, _dna(corpus_size=10, avg_length=130), "instagram")
    assert r["score"] < 30
    assert r["breakdown"]["cta"] == 0
    assert r["breakdown"]["length"] == 0


def test_cta_strong_vs_weak() -> None:
    strong = compute_virality_score("Visita el sitio. Reservá ahora", _dna(), "instagram")
    weak = compute_virality_score("Visita el sitio. Contáctanos", _dna(), "instagram")
    assert strong["breakdown"]["cta"] == 25
    assert weak["breakdown"]["cta"] == 12


def test_length_uses_dna_when_corpus_strong() -> None:
    # DNA corpus_size=10 + avg=50 · texto 50 palabras = perfect match
    text = "palabra " * 50
    dna_strong = _dna(corpus_size=10, avg_length=50)
    r = compute_virality_score(text, dna_strong, "instagram")
    assert r["breakdown"]["length"] == 25  # ±30% de 50


def test_length_falls_back_to_platform_when_dna_weak() -> None:
    # DNA corpus_size=2 (<5) → usa platform default · linkedin=400
    text = "palabra " * 400
    dna_weak = _dna(corpus_size=2, avg_length=10)
    r = compute_virality_score(text, dna_weak, "linkedin")
    assert r["breakdown"]["length"] == 25
