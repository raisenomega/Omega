"""Pydantic models · POST /content-lab/generate + /generate-image + /generate-video."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class GenerateTextRequest(BaseModel):
    platform: str = Field(..., max_length=32)
    content_type: str = Field(..., max_length=32)  # caption|hashtags|video_script
    topic: str = Field(..., min_length=1, max_length=2000)
    tone: str = Field(..., max_length=32)
    variations: int = Field(default=1, ge=1, le=3)  # legacy · usado si variation_labels ausente
    variation_labels: Optional[list[str]] = Field(default=None)  # Opción A · subset de A/B/C · MANDA sobre `variations`
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt base64
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor

    @field_validator("variation_labels")
    @classmethod
    def _check_labels(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        if not v:
            raise ValueError("variation_labels no puede ser lista vacía")
        if len(v) > 3:
            raise ValueError("variation_labels admite máximo 3 items")
        if any(x not in ("A", "B", "C") for x in v):
            raise ValueError("variation_labels solo admite 'A', 'B', 'C'")
        if len(set(v)) != len(v):
            raise ValueError("variation_labels no admite duplicados")
        return v


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
    aspect_ratio: str = Field(default="1:1", max_length=8)  # 1:1|4:5|9:16|16:9 (UX-3 · 4:5=feed IG vertical A7)
    reference_image_b64: Optional[str] = Field(default=None)  # base64 sin prefix data: (UX-6)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt como contexto extra
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor
    apply_logo: bool = Field(default=False)  # Fase 1 · opt-in · overlay del logo del cliente (default: sin logo)


class GenerateImageResponse(BaseModel):
    id: str
    content_type: str  # "image"
    generated_text: str  # URL pública generated-images/{client_id}/{uuid}.{ext}


# DEBT-IMAGE-ASYNC F3 · respuestas del modo async (flag IMAGE_ASYNC_ENABLED ON)
class ImageJobStartResponse(BaseModel):
    job_id: str
    status: str  # 'pending'


class ImageJobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending|running|completed|failed|cancelled
    image_url: Optional[str] = None
    error: Optional[str] = None
    content_id: Optional[str] = None  # fila content_lab_generated del worker · el front la usa para Guardar (BUG 11 jun)


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    ratio: str = Field(default="1280:768", max_length=32)  # legacy raw resolution
    aspect_ratio: Optional[str] = Field(default=None, max_length=8)  # 1:1|9:16|16:9 (UX-3)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005 · si presente, usar este (multi-client reseller)
    reference_attachment_b64: Optional[str] = Field(default=None)  # DEBT-CL-020 · PDF/docx/md/txt como contexto extra
    reference_mime_type: Optional[str] = Field(default=None)       # MIME del attachment para branch extractor
    apply_logo: bool = Field(default=False)  # DEBT-FFMPEG · opt-in · overlay del logo del cliente en el video


class VideoJobStartResponse(BaseModel):
    job_id: str
    status: str  # "pending"


class VideoJobStatusResponse(BaseModel):
    job_id: str
    status: str  # pending|running|completed|failed
    video_url: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = {}


class CarouselSlide(BaseModel):
    order: Optional[int] = None
    slide_type: Optional[str] = None  # portada|punto|cierre|cta
    text: str          # copy EN la placa · español
    visual_note: str   # instrucción inglés para el generador (A2) · garantizado no-vacío por el backstop


class GenerateCarouselScriptRequest(BaseModel):
    """A1.2 · guion del carrusel · `idea` por su PROPIO campo (max 4000) · NO el prompt de imagen (2000) → sin 422."""
    idea: str = Field(..., min_length=1, max_length=4000)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005
    n_slides: Optional[int] = Field(default=5, ge=3, le=10)  # D5 · default 5 · rango 3-10
    tone: Optional[str] = Field(default=None, max_length=32)


class GenerateCarouselScriptResponse(BaseModel):
    carousel_title: str
    slides: list[CarouselSlide]


class GenerateCarouselRenderRequest(BaseModel):
    """A2.4 · renderiza el guion (editado en el front) a N placas · slides 3-10 (D5 por Pydantic)."""
    carousel_title: str = Field(..., min_length=1, max_length=200)
    slides: list[CarouselSlide] = Field(..., min_length=3, max_length=10)
    client_id: Optional[str] = Field(default=None)  # DEBT-CL-005


class GenerateCarouselRenderResponse(BaseModel):
    id: str
    content_type: str  # "carousel"
    carousel_title: str
    media_urls: list[str]  # N URLs de las placas (el front renderiza el carrusel · Pieza 2 lo agenda)


class ImprovePromptRequest(BaseModel):
    original_prompt: str = Field(..., min_length=1, max_length=2000)
    platform: Optional[str] = Field(default=None, max_length=32)
    content_type: Optional[str] = Field(default=None, max_length=32)


class ImprovePromptResponse(BaseModel):
    improved_prompt: str


class ResearchRequest(BaseModel):
    """POST /content-lab/research · Brave Search wrapper · Sprint 3."""
    query: str = Field(..., min_length=3, max_length=300)
    max_results: int = Field(default=5, ge=1, le=5)  # Brave tool clamp 1-5


class ResearchResult(BaseModel):
    title: str
    url: str
    snippet: str  # cap 1000 chars desde web_search_tool


class ResearchResponse(BaseModel):
    query: str
    results: list[ResearchResult]
    answer: Optional[str] = None        # Brave "altered query" si reescribió
    count: int
    duration_ms: int
