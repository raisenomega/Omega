"""Modelos Pydantic v2 · Intelligence web-analysis + respuesta de analytics sociales.
Los modelos de datos del panel (GrowthPoint/EngagementRow/series/HeatmapCell) viven en
_analytics_models.py (split por C4) y se re-exportan aquí → importadores existentes intactos."""
from typing import Optional

from pydantic import BaseModel, Field

from app.api.routes.intelligence._analytics_models import (  # noqa: F401 · re-export (usados abajo)
    EngagementRow, EngagementSeriesPoint, GrowthPoint, HeatmapCell, PostsSeriesPoint)


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


class AeoCheckResponse(BaseModel):
    """Answer Engine Optimization · FAQ del vertical y cobertura del sitio."""
    analyzed: bool = False
    questions: list[str] = Field(default_factory=list)
    answered: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    cached: bool = False
    generated_at: Optional[str] = None
    message: Optional[str] = None


class SocialAnalyticsResponse(BaseModel):
    """Analytics sociales reales del negocio vía Zernio (DEBT-034 · "paridad de verdad" · cero-sintéticos).

    connected=False + message → negocio sin profileId (empty honesto, NO ceros que finjan datos).
    total_followers ← Σ followersCount por profileId (snapshot real) · best_hour ← slot real (derivado).
    ER de perfil = histórico (Σinter/Σreach · None si reach=0 · NUNCA comparable con Zernio). Series
    (engagement/posts) ACUMULADO: la API no tiene ventana. Arrays/None vacíos si Zernio no da dato.
    """
    connected: bool = False
    growth: list[GrowthPoint] = Field(default_factory=list)
    engagement: list[EngagementRow] = Field(default_factory=list)
    engagement_series: list[EngagementSeriesPoint] = Field(default_factory=list)
    posts_series: list[PostsSeriesPoint] = Field(default_factory=list)
    heatmap: list[HeatmapCell] = Field(default_factory=list)
    total_followers: Optional[int] = None
    total_reach: Optional[int] = None
    profile_engagement: Optional[float] = None  # engagement promedio HISTÓRICO (Σinter/Σreach·100) · '—' si reach=0
    best_hour: Optional[str] = None
    message: Optional[str] = None


class ChipResponse(BaseModel):
    """Chip Meta/Google (Fase 2) · honesto (regla cero-mocks).

    connected=False + message → cliente sin token (CTA "Conectá ..."). NUNCA métricas falsas:
    metrics solo trae enteros REALES de la API del proveedor (followers/engagement/reach o
    sessions/clicks/impressions). Si la API falla o no devuelve datos → connected=True/False
    según el token, metrics=None y message explica el porqué (nunca un número inventado).
    """
    connected: bool = False
    metrics: Optional[dict[str, int]] = None
    message: Optional[str] = None
