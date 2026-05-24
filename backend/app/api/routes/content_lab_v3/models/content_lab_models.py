"""Pydantic models · POST /content-lab/generate + /generate-image + /generate-video."""
from typing import Optional
from pydantic import BaseModel, Field


class GenerateTextRequest(BaseModel):
    platform: str = Field(..., max_length=32)
    content_type: str = Field(..., max_length=32)  # caption|hashtags|video_script
    topic: str = Field(..., min_length=1, max_length=2000)
    tone: str = Field(..., max_length=32)
    variations: int = Field(default=1, ge=1, le=3)  # PRO/enterprise desbloquea >1
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt base64
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor


class VariationItem(BaseModel):
    id: str
    label: str  # "A" | "B" | "C"
    temperature: float
    generated_text: str
    virality_score: int = 0
    virality_estimated: bool = True
    brand_dna_score: float = 0.0  # 0.0-1.0 · 0 si corpus vacío (Sprint 1 ④)


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
    aspect_ratio: str = Field(default="1:1", max_length=8)  # 1:1|9:16|16:9 (UX-3)
    reference_image_b64: Optional[str] = Field(default=None)  # base64 sin prefix data: (UX-6)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt como contexto extra
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor


class GenerateImageResponse(BaseModel):
    id: str
    content_type: str  # "image"
    generated_text: str  # URL pública generated-images/{client_id}/{uuid}.{ext}


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    ratio: str = Field(default="1280:768", max_length=32)  # legacy raw resolution
    aspect_ratio: Optional[str] = Field(default=None, max_length=8)  # 1:1|9:16|16:9 (UX-3)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt como contexto extra
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor


class VideoJobStartResponse(BaseModel):
    job_id: str
    status: str  # "pending"


class VideoJobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending|running|completed|failed
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = {}


class ImprovePromptRequest(BaseModel):
    original_prompt: str = Field(..., min_length=1, max_length=2000)
    platform: Optional[str] = Field(default=None, max_length=32)
    content_type: Optional[str] = Field(default=None, max_length=32)


class ImprovePromptResponse(BaseModel):
    improved_prompt: str
