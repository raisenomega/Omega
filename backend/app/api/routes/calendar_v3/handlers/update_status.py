"""PATCH /api/v1/calendar/{post_id}/status · transiciones user-iniciadas.

Permitidas: pending<->cancelled (cancelar/reactivar) · pending->published_manual
(el operador marca el post como publicado a mano · feature popup calendario).
Bloqueadas: cualquier otra (publishing/published/failed son sistema · DEBT futura).
INSERT behavioral_events('post_status_changed') best-effort.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.calendar_v3 import _calendar_reader as reader, _calendar_repository as repo
from app.api.routes.calendar_v3.models.calendar_models import UpdateStatusRequest

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_TRANSITIONS = {
    ("pending", "cancelled"), ("cancelled", "pending"),
    ("pending", "published_manual"),
}


@router.patch("/{post_id}/status")
async def update_post_status(
    post_id: str,
    request: UpdateStatusRequest,
    authorization: Optional[str] = Header(None),
) -> dict:
    user = await get_current_user(authorization)
    post = reader.get_scheduled_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")
    accessible = reader.get_accessible_client_ids(user["id"])
    if str(post.get("client_id")) not in accessible:
        raise HTTPException(status_code=403, detail="access_denied")

    current = str(post.get("status") or "")
    new = request.status
    if (current, new) not in ALLOWED_TRANSITIONS:
        raise HTTPException(status_code=422, detail=f"invalid_transition:{current}->{new}")

    try:  # write crítico · NO best-effort · si falla (CHECK / 0 filas) surfacea 500, no miente 200
        updated = repo.update_status(post_id, new)
    except Exception as e:
        logger.error(f"update_status failed · post_id={post_id} · {current}->{new} · {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="status_update_failed")
    repo.safe_insert("behavioral", repo.insert_behavioral_status_change,  # telemetría · best-effort OK
                     user["id"], str(post["client_id"]), post_id, current, new)
    return {"id": post_id, "status": str(updated.get("status") or new)}
