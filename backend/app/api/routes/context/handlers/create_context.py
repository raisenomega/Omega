"""Handler: Create context document"""
import logging
from typing import Dict, Any
from fastapi import HTTPException
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_create_context(request) -> Dict[str, Any]:
    """Create new context document from JSON body."""
    try:
        if request.scope not in ["global", "client", "department"]:
            raise HTTPException(400, "Invalid scope. Must be: global, client, or department")
        if request.scope != "global" and not request.scope_id:
            raise HTTPException(400, f"scope_id required for scope={request.scope}")
        # Detect raw PDF binary (should be extracted text, not binary)
        if request.content.startswith('%PDF'):
            raise HTTPException(422, "El contenido parece ser un PDF sin procesar. Usa el endpoint /extract-url/ o sube el texto extraído.")
        # Remove null characters (second line of defense)
        content = request.content.replace('\u0000', '').replace('\x00', '')
        supabase = get_supabase_service()
        resp = supabase.client.table("context_library").insert({
            "name": request.name,
            "content": content,
            "scope": request.scope,
            "scope_id": request.scope_id,
            "tags": request.tags or [],
            "file_type": request.file_type or "text",
            "created_by": "ibrain"
        }).execute()
        if not resp.data:
            raise HTTPException(500, "Failed to create context")
        doc = resp.data[0]
        # Auto-clear cache so NOVA gets fresh context immediately
        import app.services.context_service as ctx_module
        ctx_module._global_cache = None
        ctx_module._global_cache_time = None
        logger.info(f"Created context: {request.name} (scope={request.scope}) - cache cleared")
        return doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create context: {e}")
        raise HTTPException(500, f"Failed to create context: {str(e)}")
