"""Pydantic models · POST /content-lab/generate + /generate-image + /generate-video."""
from typing import Optional
from pydantic import BaseModel, Field


class GenerateTextRequest(BaseModel):
    platform: str = Field(..., max_length=32)
    content_type: str = Field(..., max_length=32)  # caption|hashtags|video_script
    topic: str = Field(..., min_length=1, max_length=2000)
    tone: str = Field(..., max_length=32)
    variations: int = Field(default=1, ge=1, le=3)  # PRO/enterprise desbloquea >1


class VariationItem(BaseModel):
    id: str
    label: str  # "A" | "B" | "C"
    temperature: float
    generated_text: str
    virality_score: int = 0
    virality_estimated: bool = True


class GenerateTextResponse(BaseModel):
    id: str
    content_type: str
    generated_text: str
    virality_score: int = 0          # = variations[0].virality_score (legacy)
    virality_estimated: bool = True  # P1 · True hasta Meta API real (Sprint 3+)
    variations: list[VariationItem] = []  # nuevo Sprint 2 P2 · siempre poblado (n=1 ó 3)


class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    style: str = Field(default="realistic", max_length=32)  # realistic|cartoon|minimal


class GenerateImageResponse(BaseModel):
    id: str
    content_type: str  # "image"
    generated_text: str  # URL pública generated-images/{client_id}/{uuid}.{ext}


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    ratio: str = Field(default="1280:768", max_length=32)  # 1280:768|768:1280


class VideoJobStartResponse(BaseModel):
    job_id: str
    status: str  # "pending"


class VideoJobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending|running|completed|failed
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = {}
