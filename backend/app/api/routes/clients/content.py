"""
Client Content Endpoint
GET /clients/{client_id}/content/ - List content generated for client
"""
from fastapi import APIRouter, Header, Query
from typing import Optional
from app.api.routes.clients.handlers import handle_get_client_content
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


@router.get("/{client_id}/content/")
async def get_client_content(
    client_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None, alias="type"),
    authorization: Optional[str] = Header(None)
):
    """Get content generated for this client"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_client_content(client_id, limit, offset, type)
