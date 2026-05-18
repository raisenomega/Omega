"""
Performance Handler — Update prompt performance scores based on engagement.
DDD: Application layer - performance tracking.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository
from ..models import PerformanceUpdateRequest
import logging

logger = logging.getLogger(__name__)


async def handle_update_performance(
    prompt_id: str,
    request: PerformanceUpdateRequest
) -> dict:
    """
    Actualiza el performance_score de un prompt basado en engagement real.

    Formula: new_score = (old_score * 0.7) + (engagement_rate * 10 * 0.3)

    Args:
        prompt_id: UUID del prompt
        engagement_rate: Tasa de engagement real (0.0 a 1.0, ej: 0.045 = 4.5%)
    """
    try:
        supabase = get_supabase_service()
        vault_repo = PromptVaultRepository(supabase)

        # Update performance score
        await vault_repo.update_performance_score(
            prompt_id=prompt_id,
            engagement_rate=request.engagement_rate
        )

        # Get updated prompt
        updated_prompt = await vault_repo.get_prompt_by_id(prompt_id)

        if not updated_prompt:
            raise HTTPException(404, f"Prompt {prompt_id} not found after update")

        logger.info(
            f"Updated performance for prompt {prompt_id}: "
            f"engagement={request.engagement_rate:.4f}, "
            f"new_score={updated_prompt['performance_score']:.2f}"
        )

        return {
            "prompt_id": prompt_id,
            "engagement_rate": request.engagement_rate,
            "new_performance_score": updated_prompt["performance_score"],
            "engagement_avg": updated_prompt["engagement_avg"],
            "times_used": updated_prompt["times_used"],
            "updated": True
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating performance for {prompt_id}: {e}")
        raise HTTPException(500, f"Error updating performance: {str(e)}")
