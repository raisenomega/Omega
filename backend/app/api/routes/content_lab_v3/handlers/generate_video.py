"""POST /api/v1/content-lab/generate-video + GET .../generate-video/{job_id}

DEBT-020 (Sprint 2) · background job pattern. POST retorna job_id inmediato ·
worker APScheduler 'date' trigger ejecuta start+poll+download+upload en background.
GET retorna status actual · frontend debe poll cada 5s hasta completed|failed.

404 si job no existe O no es del cliente actual (no leak existence sobre jobs ajenos).
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateVideoRequest, VideoJobStartResponse, VideoJobStatusResponse,
)
from app.bc_cognition.application.use_video_job import create_video_job, get_video_job

router = APIRouter()


@router.post("/generate-video", response_model=VideoJobStartResponse)
async def start_video_generation(
    request: GenerateVideoRequest,
    authorization: Optional[str] = Header(None),
) -> VideoJobStartResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    client_id = str(client["id"])
    job_id = await create_video_job(client_id, request.prompt, request.ratio)
    if not job_id:
        raise HTTPException(status_code=503, detail="job_create_failed")
    return VideoJobStartResponse(job_id=job_id, status="pending")


@router.get("/generate-video/{job_id}", response_model=VideoJobStatusResponse)
async def get_video_job_status(
    job_id: str,
    authorization: Optional[str] = Header(None),
) -> VideoJobStatusResponse:
    user = await get_current_user(authorization)
    client = repo.find_client_for_user(user["id"])
    if not client:
        raise HTTPException(status_code=403, detail="no_client_for_user")
    job = get_video_job(job_id)
    if not job or str(job.get("client_id")) != str(client["id"]):
        raise HTTPException(status_code=404, detail="job_not_found")
    return VideoJobStatusResponse(
        job_id=job_id, status=job["status"],
        video_url=job.get("video_url"), error=job.get("error"),
        metadata=job.get("metadata") or {},
    )
