"""
Domain types para sistema multi-LLM.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

# Content types disponibles
ContentType = Literal[
    "post", "caption", "story", "reel", "hashtags",
    "email", "anuncio", "bio", "script", "carrusel",
    "analytics", "ad"
]

# User tiers basados en planes reales
UserTier = Literal["basico_97", "pro_197", "enterprise_497"]

# Acciones de validación de uso
UsageAction = Literal["allow", "warn", "upsell", "block"]

# Providers de LLM · §2.6: Anthropic-only para texto (DDD I1)
LLMProvider = Literal["anthropic"]

class LLMConfig(BaseModel):
    """Configuración de un modelo LLM."""
    primary: str = Field(..., description="Modelo primario (ej: anthropic/claude-sonnet-4-6)")
    fallback: List[str] = Field(default_factory=list, description="Modelos de respaldo")
    cache: bool = Field(default=False, description="Activar context caching")

class LLMResponse(BaseModel):
    """Respuesta de generación LLM."""
    content: str
    provider: str
    model: str
    cached: bool
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None

class TierConfig(BaseModel):
    """Configuración completa de un tier."""
    post: Optional[LLMConfig] = None
    caption: LLMConfig
    story: Optional[LLMConfig] = None
    reel: Optional[LLMConfig] = None
    hashtags: LLMConfig
    email: Optional[LLMConfig] = None
    anuncio: Optional[LLMConfig] = None
    bio: Optional[LLMConfig] = None
    script: LLMConfig
    carrusel: Optional[LLMConfig] = None
    analytics: Optional[LLMConfig] = None
    ad: Optional[LLMConfig] = None
    imagen: LLMConfig
