"""Content Lab — content management and analytics routes."""
from fastapi import APIRouter, Query

from .models import ContentListResponse, DeleteContentResponse
from .handlers import (
    handle_list_content,
    handle_delete_content,
    handle_analyze_insight,
    handle_analyze_forecast,
    handle_predict_virality,
)

content_router = APIRouter()


@content_router.get("/", response_model=ContentListResponse)
async def list_content(
    client_id: str,
    content_type: str = None,
    limit: int = 20,
    offset: int = 0,
) -> ContentListResponse:
    return await handle_list_content(client_id, content_type, limit, offset)


@content_router.delete("/{content_id}/", response_model=DeleteContentResponse)
async def delete_content(content_id: str) -> DeleteContentResponse:
    return await handle_delete_content(content_id)


@content_router.post("/analyze-insight/")
async def analyze_insight(
    content: str = Query(...),
    content_type: str = Query(...),
    platform: str = Query(default="instagram"),
):
    return await handle_analyze_insight(content, content_type, platform)


@content_router.post("/analyze-forecast/")
async def analyze_forecast(
    content: str = Query(...),
    content_type: str = Query(...),
    platform: str = Query(default="instagram"),
    avg_followers: int = Query(default=5000),
):
    return await handle_analyze_forecast(content, content_type, platform, avg_followers)


@content_router.post("/analyze-virality/")
async def analyze_virality(
    content: str = Query(...),
    content_type: str = Query(...),
    platform: str = Query(default="instagram"),
):
    return await handle_predict_virality(content, content_type, platform)
