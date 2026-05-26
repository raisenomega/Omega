"""PATCH /api/v1/aria/suggestions/{suggestion_id}/read · marca leída.

Ownership: la sugerencia debe pertenecer a un cliente del user (resolve_client_or_403
con el client_id de la fila · 403/404 si no). Escritura con service_role.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.bc_cognition.infrastructure import _suggestions_writer as writer

router = APIRouter()


@router.patch("/suggestions/{suggestion_id}/read")
async def aria_suggestions_read(
    suggestion_id: str,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    suggestion = writer.get_suggestion(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="suggestion_not_found")
    # Ownership: raise 403/404 si el client_id de la fila no pertenece al user.
    resolve_client_or_403(user["id"], str(suggestion["client_id"]))
    if not writer.mark_read(suggestion_id):
        raise HTTPException(status_code=503, detail="mark_read_failed")
    return {"marked_read": True}
