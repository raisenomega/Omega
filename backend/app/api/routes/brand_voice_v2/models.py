"""Pydantic models para brand_voice_v2 routes (Sprint 2 ②.A · GET /summary).

Read-only · sin write/edit · alimenta página /brand-voice del cliente.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CorpusEntry(BaseModel):
    text: str
    platform: Optional[str] = None
    created_at: str


class KeywordCount(BaseModel):
    keyword: str
    count: int = Field(..., ge=1)


class BrandVoiceSummaryResponse(BaseModel):
    corpus_count: int = Field(..., ge=0)
    latest_approvals: list[CorpusEntry] = Field(default_factory=list)
    top_keywords: list[KeywordCount] = Field(default_factory=list)
