"""BrandDNA · value object inmutable derivado del brand_voice_corpus.

Producido por application._brand_dna_builder · consumido por
content_lab_v3 para enriquecer system prompt de RAFA (Tarea 3 Sprint 1).
"""
from dataclasses import dataclass
from typing import Literal


ConfidenceLabel = Literal["weak", "emerging", "strong"]


@dataclass(frozen=True)
class BrandDNA:
    tone: list[str]
    keywords: list[tuple[str, int]]
    avg_length_words: int
    top_post_excerpts: list[str]
    corpus_size: int
    score: float

    def confidence_label(self) -> ConfidenceLabel:
        if self.score >= 0.7:
            return "strong"
        if self.score >= 0.3:
            return "emerging"
        return "weak"

    def is_strong(self) -> bool:
        return self.score >= 0.7

    def is_weak(self) -> bool:
        return self.score < 0.3

    @staticmethod
    def empty() -> "BrandDNA":
        return BrandDNA([], [], 0, [], 0, 0.0)

    def to_dict(self) -> dict:
        """Serializa a dict JSON-able (tuples → lists). Para jsonb storage."""
        return {
            "tone": list(self.tone),
            "keywords": [list(kw) for kw in self.keywords],
            "avg_length_words": self.avg_length_words,
            "top_post_excerpts": list(self.top_post_excerpts),
            "corpus_size": self.corpus_size,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "BrandDNA":
        """Deserializa desde dict (jsonb de Supabase). Listas [w, n] → tuples."""
        return cls(
            tone=list(d.get("tone") or []),
            keywords=[tuple(kw) for kw in (d.get("keywords") or [])],
            avg_length_words=int(d.get("avg_length_words", 0)),
            top_post_excerpts=list(d.get("top_post_excerpts") or []),
            corpus_size=int(d.get("corpus_size", 0)),
            score=float(d.get("score", 0.0)),
        )
