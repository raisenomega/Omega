"""
Create/Update/Delete Handlers — Write operations for prompt vault.
DDD: Application layer - write operations.
Strict <200L per file.
"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
from ..models import PromptVaultCreate, PromptVaultUpdate
import logging

logger = logging.getLogger(__name__)


async def handle_create_prompt(request: PromptVaultCreate) -> dict:
    """
    Crea un nuevo prompt en el vault.
    Requiere permisos de admin.
    """
    try:
        supabase = get_supabase_service()

        response = supabase.client.table("prompt_vault").insert(
            request.dict()
        ).execute()

        if not response.data:
            raise HTTPException(500, "Failed to create prompt")

        logger.info(
            f"Created new prompt: {request.name} "
            f"({request.vertical}/{request.category}/{request.platform})"
        )

        return response.data[0]

    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(500, f"Error creating prompt: {str(e)}")


async def handle_update_prompt(prompt_id: str, request: PromptVaultUpdate) -> dict:
    """
    Actualiza un prompt existente.
    Solo actualiza los campos proporcionados.
    """
    try:
        supabase = get_supabase_service()

        # Get update data (exclude unset fields)
        update_data = request.dict(exclude_unset=True)

        if not update_data:
            raise HTTPException(400, "No fields to update")

        # Always update last_updated
        update_data["last_updated"] = "now()"

        response = supabase.client.table("prompt_vault").update(
            update_data
        ).eq("id", prompt_id).execute()

        if not response.data:
            raise HTTPException(404, f"Prompt {prompt_id} not found")

        logger.info(f"Updated prompt {prompt_id}: {list(update_data.keys())}")

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt {prompt_id}: {e}")
        raise HTTPException(500, f"Error updating prompt: {str(e)}")


async def handle_delete_prompt(prompt_id: str) -> dict:
    """
    Soft delete de un prompt (marca como is_active=false).
    No elimina físicamente del vault.
    """
    try:
        supabase = get_supabase_service()

        response = supabase.client.table("prompt_vault").update({
            "is_active": False,
            "last_updated": "now()"
        }).eq("id", prompt_id).execute()

        if not response.data:
            raise HTTPException(404, f"Prompt {prompt_id} not found")

        logger.info(f"Soft deleted prompt {prompt_id}")

        return {
            "id": prompt_id,
            "deleted": True,
            "message": "Prompt marcado como inactivo"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt {prompt_id}: {e}")
        raise HTTPException(500, f"Error deleting prompt: {str(e)}")
