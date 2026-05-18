"""
List and Get Handlers — Query operations for prompt vault.
DDD: Application layer - read operations.
Strict <200L per file.
"""
from fastapi import HTTPException
from typing import Optional
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository
import logging

logger = logging.getLogger(__name__)


async def handle_list_prompts(
    vertical: Optional[str],
    category: Optional[str],
    platform: Optional[str],
    agent_code: Optional[str],
    is_active: Optional[bool],
    min_score: Optional[float],
    limit: int,
    offset: int
) -> dict:
    """
    Lista prompts del vault con filtros opcionales.
    Ordenado por performance_score descendente.
    """
    try:
        supabase = get_supabase_service()
        query = supabase.client.table("prompt_vault").select("*", count="exact")

        # Apply filters
        if vertical:
            query = query.eq("vertical", vertical)
        if category:
            query = query.eq("category", category)
        if platform:
            query = query.eq("platform", platform)
        if agent_code:
            query = query.eq("agent_code", agent_code)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        if min_score is not None:
            query = query.gte("performance_score", min_score)

        # Execute with pagination
        response = query.order(
            "performance_score", desc=True
        ).range(offset, offset + limit - 1).execute()

        total = response.count if hasattr(response, 'count') else len(response.data)

        return {
            "prompts": response.data,
            "total": total
        }

    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(500, f"Error listing prompts: {str(e)}")


async def handle_get_prompt(prompt_id: str) -> dict:
    """
    Obtiene un prompt específico por ID.
    """
    try:
        supabase = get_supabase_service()
        vault_repo = PromptVaultRepository(supabase)

        prompt = await vault_repo.get_prompt_by_id(prompt_id)

        if not prompt:
            raise HTTPException(404, f"Prompt {prompt_id} not found")

        return prompt

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prompt {prompt_id}: {e}")
        raise HTTPException(500, f"Error fetching prompt: {str(e)}")
