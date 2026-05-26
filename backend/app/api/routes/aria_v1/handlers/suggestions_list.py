"""GET /api/v1/aria/suggestions · lista sugerencias del cliente (created_at desc).

Resuelve cliente (access control) · filtra is_read=false si unread_only.
Lectura vía service_role (_suggestions_repository) tras autorizar al user (P1).
"""
from typing import Optional
from fastapi import APIRouter, Header, Query
from app.api.routes.aria_v1.models import ARIASuggestion, ARIASuggestionsResponse
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_cognition.infrastructure import _suggestions_writer as writer

router = APIRouter()


@router.get("/suggestions", response_model=ARIASuggestionsResponse)
async def aria_suggestions_list(
    authorization: Optional[str] = Header(None),
    client_id: Optional[str] = Query(None),
    unread_only: bool = Query(False),
) -> ARIASuggestionsResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], client_id)
    rows = writer.list_suggestions(str(client["id"]), unread_only=unread_only)
    return ARIASuggestionsResponse(
        suggestions=[ARIASuggestion(**r) for r in rows], generated=0,
    )
