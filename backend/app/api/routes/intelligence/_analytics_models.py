"""Modelos de datos del panel Analytics (separado de models.py por C4 · ratchet en baja).
Conteos REALES de Zernio · acumulado (NO ventana 'this period') · sin %. SocialAnalyticsResponse
(en models.py) los compone. Re-exportados por models.py → los importadores existentes no cambian."""
from pydantic import BaseModel


class GrowthPoint(BaseModel):
    """Punto de la serie de seguidores (IG · GrowthChart)."""
    date: str
    followers: int


class EngagementRow(BaseModel):
    """Engagement por plataforma acumulado (conteos REALES · sin %)."""
    platform: str
    likes: int
    comments: int
    shares: int
    saves: int
    views: int
    reach: int = 0


class EngagementSeriesPoint(BaseModel):
    """Punto diario de engagement (8 campos · de dailyData.metrics · acumulado · NO ventana)."""
    date: str
    impressions: int = 0
    reach: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    views: int = 0


class PostsSeriesPoint(BaseModel):
    """Publicaciones por día (postCount real · acumulado · NO 'this period')."""
    date: str
    count: int


class HeatmapCell(BaseModel):
    """Celda de mejores horas (BestTimesHeatmap agrupa por hora)."""
    day: str
    hour: int
    value: float
