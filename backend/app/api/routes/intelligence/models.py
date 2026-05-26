"""Modelos Pydantic v2 · Intelligence web-analysis."""
from typing import Optional

from pydantic import BaseModel, Field


class WebAnalysisResponse(BaseModel):
    """Resultado de análisis web · honesto (analyzed=False + message si no aplica)."""
    url: Optional[str] = None
    analyzed: bool = False
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1: list[str] = Field(default_factory=list)
    h2: list[str] = Field(default_factory=list)
    h3: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    score: int = 0
    recommendations: list[str] = Field(default_factory=list)
    cached: bool = False
    generated_at: Optional[str] = None
    message: Optional[str] = None


class GeoCheckResponse(BaseModel):
    """Visibilidad GEO/AEO · honesto (analyzed=False + message si no aplica)."""
    status: str = "unknown"
    summary: Optional[str] = None
    tips: list[str] = Field(default_factory=list)
    queries: list[str] = Field(default_factory=list)
    analyzed: bool = False
    cached: bool = False
    generated_at: Optional[str] = None
    message: Optional[str] = None
