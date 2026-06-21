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


class GrowthPoint(BaseModel):
    """Punto de la serie de seguidores (IG · GrowthChart)."""
    date: str
    followers: int


class EngagementRow(BaseModel):
    """Engagement por plataforma del período (conteos REALES · sin %)."""
    platform: str
    likes: int
    comments: int
    shares: int
    saves: int
    views: int


class HeatmapCell(BaseModel):
    """Celda de mejores horas (BestTimesHeatmap agrupa por hora)."""
    day: str
    hour: int
    value: float


class SocialAnalyticsResponse(BaseModel):
    """Analytics sociales reales del negocio vía Zernio (DEBT-034 · "paridad de verdad" · cero-sintéticos).

    connected=False + message → negocio sin profileId (empty honesto, NO ceros que finjan datos).
    total_followers ← Σ followersCount por profileId (snapshot real) · best_hour ← slot real (derivado).
    SIN porcentaje de engagement Y SIN KPI Posts (decisión P1: la API no expone ER por-post ni ventana
    'this period' · solo conteos por red). Arrays/None vacíos si Zernio no da dato · data_delay ~24-48h.
    """
    connected: bool = False
    growth: list[GrowthPoint] = Field(default_factory=list)
    engagement: list[EngagementRow] = Field(default_factory=list)
    heatmap: list[HeatmapCell] = Field(default_factory=list)
    total_followers: Optional[int] = None
    best_hour: Optional[str] = None
    data_delay: Optional[str] = None
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
