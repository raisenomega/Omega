"""
Domain types para sistema de memoria persistente.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MemoryMetadata(BaseModel):
    """Metadata de una memoria."""
    source: str = Field(default="omega", description="Fuente de la memoria")
    type: str = Field(default="client_interaction", description="Tipo de memoria")
    platform: Optional[str] = Field(None, description="Plataforma social")
    content_type: Optional[str] = Field(None, description="Tipo de contenido")
    model_used: Optional[str] = Field(None, description="Modelo LLM usado")


class MemoryEntry(BaseModel):
    """Entrada de memoria individual."""
    user_id: str = Field(..., description="ID del usuario (client_123)")
    content: str = Field(..., description="Contenido de la memoria")
    metadata: MemoryMetadata = Field(..., description="Metadata adicional")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")


class MemorySearchResult(BaseModel):
    """Resultado de búsqueda de memoria."""
    memory: str = Field(..., description="Texto de la memoria")
    score: float = Field(..., description="Score de relevancia (0-1)")
    metadata: dict[str, str] = Field(default_factory=dict, description="Metadata")


class MemorySearchResponse(BaseModel):
    """Response de búsqueda en memoria."""
    results: list[MemorySearchResult] = Field(
        default_factory=list,
        description="Memorias encontradas"
    )
    total: int = Field(default=0, description="Total de resultados")


class ClientMemoryContext(BaseModel):
    """Contexto de memoria para un cliente."""
    client_id: str = Field(..., description="ID del cliente")
    memories: list[str] = Field(
        default_factory=list,
        description="Memorias relevantes"
    )
    formatted_context: str = Field(
        default="",
        description="Contexto formateado para inyectar en prompt"
    )


# Configuración de mem0
MEM0_CONFIG = {
    "version": "v1.1",
    "vector_store_provider": "qdrant",
    "llm_provider": "litellm",
    "llm_model": "anthropic/claude-haiku-4-5-20251001",  # extracción de memoria (I1 · Anthropic-only)
    "collection_name": "omega_client_memories"
}

# Configuración de Qdrant
QDRANT_CONFIG = {
    "collection_name": "omega_client_memories",
    "vector_size": 1536,  # embeddings 1536 dims
    "distance": "Cosine"
}
