"""POST /api/v1/publish/auto · ejecuta la auto-publicación real (Publicador agent).

Auth cliente (JWT). Resuelve el client propio del usuario y publica de verdad un
scheduled_post YA aprobado (status='pending') vía el token Meta del cliente.

Mapeo de gates a HTTP honesto (cero fabricación):
  post_not_found            → 404
  post_access_denied        → 403
  post_not_publishable:<s>  → 409  (no se re-publica algo ya publicado/cancelado/fallido)
  meta_not_connected        → 409  (el cliente debe conectar Meta primero · OAuth RONDA D)
  meta_no_page              → 409  (token sin Page id · reconectar Meta)
Si Meta rechaza la publicación → 200 {published:false, error:<detalle Graph>} (honesto).
"""
import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.publishing._publish_service import (
    PublishGateError,
    publish_scheduled_post,
)
from app.api.routes.publishing.models import AutoPublishRequest, AutoPublishResponse

router = APIRouter()
logger = logging.getLogger(__name__)

_GATE_TO_STATUS: dict[str, int] = {
    "post_not_found": 404,
    "post_access_denied": 403,
    "meta_not_connected": 409,
    "meta_no_page": 409,
}


@router.post("/publish/auto", response_model=AutoPublishResponse, tags=["Publishing"])
async def auto_publish(
    request: AutoPublishRequest,
    authorization: Optional[str] = Header(None),
) -> AutoPublishResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])

    try:
        result = await publish_scheduled_post(request.scheduled_post_id, client_id)
    except PublishGateError as e:
        # post_not_publishable:<status> es prefijo → default 409 honesto.
        status = _GATE_TO_STATUS.get(e.code, 409)
        logger.info(f"auto-publish gate · {e.code} · post={request.scheduled_post_id} client={client_id}")
        raise HTTPException(status_code=status, detail=e.code)

    return AutoPublishResponse(
        published=result.published,
        platform_post_id=result.platform_post_id,
        error=result.error,
    )
