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
