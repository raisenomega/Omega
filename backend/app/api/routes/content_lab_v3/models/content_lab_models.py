"""Pydantic models · POST /content-lab/generate."""
from pydantic import BaseModel, Field


class GenerateTextRequest(BaseModel):
    platform: str = Field(..., max_length=32)
    content_type: str = Field(..., max_length=32)  # caption|hashtags|video_script
    topic: str = Field(..., min_length=1, max_length=2000)
    tone: str = Field(..., max_length=32)


class GenerateTextResponse(BaseModel):
    id: str
    content_type: str
    generated_text: str
