"""Handle PATCH /context/{context_id}/"""
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service
import app.services.context_service as ctx_module


async def handle_update_context(context_id: str, update_data: dict) -> dict:
    if not update_data:
        raise HTTPException(400, "No hay datos para actualizar")
    supabase = get_supabase_service()
    result = (
        supabase.client.table("context_library")
        .update(update_data)
        .eq("id", context_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Documento no encontrado")
    ctx_module._global_cache = None
    ctx_module._global_cache_time = None
    return result.data[0]
