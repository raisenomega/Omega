"""POST /api/v1/content-lab/generate-video + GET .../generate-video/{job_id}

DEBT-020 (Sprint 2) · background job pattern. POST retorna job_id inmediato ·
worker APScheduler 'date' trigger ejecuta start+poll+download+upload en background.
GET retorna status actual · frontend debe poll cada 5s hasta completed|failed.

404 si job no existe O no es del cliente actual (no leak existence sobre jobs ajenos).
"""
import logging
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3._client_resolver import resolve_client_or_403
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateVideoRequest, VideoJobStartResponse, VideoJobStatusResponse,
)
# cross-BC helper · candidato a app.shared.access_control (DEBT-CL-005)
from app.api.routes.clients_v3 import _clients_reader as clients_reader
from app.api.routes.clients_v3._access_control import user_owns_client
from app.bc_cognition.application.use_video_job import create_video_job, get_video_job
from app.bc_cognition.infrastructure import video_job_repository as job_repo

router = APIRouter()
logger = logging.getLogger(__name__)

# UX-3 · aspect ratio → raw resolution (compat con _RATIO_TO_ASPECT en _video_compat)
_ASPECT_TO_RATIO = {"1:1": "1024:1024", "9:16": "768:1280", "16:9": "1280:768"}


@router.post("/generate-video", response_model=VideoJobStartResponse)
async def start_video_generation(
    request: GenerateVideoRequest,
    authorization: Optional[str] = Header(None),
) -> VideoJobStartResponse:
    user = await get_current_user(authorization)
    client = resolve_client_or_403(user["id"], request.client_id)  # DEBT-CL-005
    client_id = str(client["id"])
    ratio = _ASPECT_TO_RATIO.get(request.aspect_ratio, request.ratio) if request.aspect_ratio else request.ratio
    try:
        job_id = await create_video_job(client_id, request.prompt, ratio)
    except Exception as e:
        logger.error(f"create_video_job failed · client={client_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"job_create_failed:{type(e).__name__}:{str(e)[:200]}",
        )
    return VideoJobStartResponse(job_id=job_id, status="pending")


@router.get("/generate-video/{job_id}", response_model=VideoJobStatusResponse)
async def get_video_job_status(
    job_id: str,
    authorization: Optional[str] = Header(None),
) -> VideoJobStatusResponse:
    user = await get_current_user(authorization)
    job = get_video_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    # DEBT-CL-005 variant · ownership via job.client_id (no via find_client_for_user
    # que ignoraba reseller multi-client). 404 sin leak existence si no owner.
    job_client = clients_reader.get_client(str(job.get("client_id") or ""))
    if not job_client or not user_owns_client(user["id"], job_client):
        raise HTTPException(status_code=404, detail="job_not_found")
    return VideoJobStatusResponse(
        job_id=job_id, status=job["status"],
        video_url=job.get("video_url"), error=job.get("error"),
        metadata=job.get("metadata") or {},
    )


@router.delete("/generate-video/{job_id}", status_code=204)
async def cancel_video_job(
    job_id: str,
    authorization: Optional[str] = Header(None),
) -> None:
    """DEBT-CL-010: user-initiated cancel · ahorra costo Veo si job sigue
    running. Idempotente (completed/failed/cancelled → 204 sin tocar)."""
    user = await get_current_user(authorization)
    job = get_video_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    job_client = clients_reader.get_client(str(job.get("client_id") or ""))
    if not job_client or not user_owns_client(user["id"], job_client):
        raise HTTPException(status_code=404, detail="job_not_found")  # no leak
    if job["status"] in ("completed", "failed", "cancelled"):
        return  # idempotent
    job_repo.update_job_cancelled(job_id)
    logger.info(f"job {job_id} cancelled · user={user['id']}")
