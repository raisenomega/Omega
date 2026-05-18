"""
Stats Handlers — Analytics and statistics for prompt vault.
DDD: Application layer - analytics operations.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository
import logging

logger = logging.getLogger(__name__)


async def handle_get_top_prompts(vertical: str, limit: int) -> dict:
    """
    Obtiene los prompts con mejor performance para un vertical específico.
    """
    try:
        supabase = get_supabase_service()
        vault_repo = PromptVaultRepository(supabase)

        top_prompts = await vault_repo.get_top_prompts(
            vertical=vertical,
            limit=limit
        )

        return {
            "vertical": vertical,
            "prompts": top_prompts,
            "count": len(top_prompts)
        }

    except Exception as e:
        logger.error(f"Error fetching top prompts for {vertical}: {e}")
        raise HTTPException(500, f"Error fetching top prompts: {str(e)}")


async def handle_get_stats() -> dict:
    """
    Obtiene estadísticas generales del Prompt Vault.
    """
    try:
        supabase = get_supabase_service()

        # Total prompts
        total_response = supabase.client.table("prompt_vault").select(
            "*", count="exact"
        ).execute()

        # Active prompts
        active_response = supabase.client.table("prompt_vault").select(
            "*", count="exact"
        ).eq("is_active", True).execute()

        # Average score
        avg_response = supabase.client.table("prompt_vault").select(
            "performance_score"
        ).eq("is_active", True).execute()

        avg_score = 0
        if avg_response.data:
            scores = [p["performance_score"] for p in avg_response.data]
            avg_score = sum(scores) / len(scores) if scores else 0

        # By vertical
        vertical_response = supabase.client.table("prompt_vault").select(
            "vertical"
        ).eq("is_active", True).execute()

        verticals = {}
        for item in vertical_response.data:
            v = item["vertical"]
            verticals[v] = verticals.get(v, 0) + 1

        return {
            "total_prompts": total_response.count if hasattr(total_response, 'count') else len(total_response.data),
            "active_prompts": active_response.count if hasattr(active_response, 'count') else len(active_response.data),
            "average_performance_score": round(avg_score, 2),
            "by_vertical": verticals
        }

    except Exception as e:
        logger.error(f"Error fetching vault stats: {e}")
        raise HTTPException(500, f"Error fetching stats: {str(e)}")
