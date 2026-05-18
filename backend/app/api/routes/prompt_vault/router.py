"""
Prompt Vault API Router — Thin delegation layer to handlers.
Filosofía: No velocity, only precision 🐢💎
DDD: API Interface layer - HTTP routing only.
Strict <200L per file.
"""
from fastapi import APIRouter, Query
from typing import Optional
from .models import (
    PromptVaultCreate,
    PromptVaultUpdate,
    PromptVaultResponse,
    PerformanceUpdateRequest,
    PromptVaultListResponse
)
from .handlers import (
    handle_list_prompts,
    handle_get_prompt,
    handle_create_prompt,
    handle_update_prompt,
    handle_delete_prompt,
    handle_update_performance,
    handle_get_top_prompts,
    handle_get_stats
)

router = APIRouter(prefix="/prompt-vault", tags=["prompt-vault"])


@router.get("/", response_model=PromptVaultListResponse)
async def list_prompts(
    vertical: Optional[str] = Query(None, description="Filter by vertical"),
    category: Optional[str] = Query(None, description="Filter by category"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    agent_code: Optional[str] = Query(None, description="Filter by agent"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    min_score: Optional[float] = Query(None, ge=0, le=10, description="Minimum performance score"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """Lista prompts del vault con filtros opcionales"""
    return await handle_list_prompts(
        vertical, category, platform, agent_code, is_active, min_score, limit, offset
    )


@router.get("/{prompt_id}", response_model=PromptVaultResponse)
async def get_prompt(prompt_id: str):
    """Obtiene un prompt específico por ID"""
    return await handle_get_prompt(prompt_id)


@router.post("/", response_model=PromptVaultResponse, status_code=201)
async def create_prompt(request: PromptVaultCreate):
    """Crea un nuevo prompt en el vault"""
    return await handle_create_prompt(request)


@router.patch("/{prompt_id}", response_model=PromptVaultResponse)
async def update_prompt(prompt_id: str, request: PromptVaultUpdate):
    """Actualiza un prompt existente"""
    return await handle_update_prompt(prompt_id, request)


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Soft delete de un prompt (marca como is_active=false)"""
    return await handle_delete_prompt(prompt_id)


@router.post("/{prompt_id}/performance")
async def update_performance(prompt_id: str, request: PerformanceUpdateRequest):
    """Actualiza el performance_score basado en engagement real"""
    return await handle_update_performance(prompt_id, request)


@router.get("/top/{vertical}")
async def get_top_prompts(
    vertical: str,
    limit: int = Query(10, ge=1, le=50)
):
    """Obtiene los prompts con mejor performance para un vertical"""
    return await handle_get_top_prompts(vertical, limit)


@router.get("/stats/summary")
async def get_stats():
    """Obtiene estadísticas generales del Prompt Vault"""
    return await handle_get_stats()
