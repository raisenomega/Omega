"""
Pydantic models for Prompt Vault API.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PromptVaultCreate(BaseModel):
    """Request model for creating a new prompt"""
    name: str = Field(..., min_length=1, max_length=255, description="Descriptive name")
    category: str = Field(..., description="Content type: caption, ad, email, script, story, post, hashtags")
    vertical: str = Field(..., description="Industry: real_estate, construction, health, restaurant, generic")
    platform: Optional[str] = Field(None, description="Platform: instagram, facebook, linkedin, tiktok, email")
    technique: str = Field(..., description="Technique: AIDA, PAS, storytelling, CoT, few-shot, etc.")
    source: str = Field(default="omega-tested", description="Source of the prompt")
    prompt_text: str = Field(..., min_length=10, description="The actual prompt template")
    example_input: Optional[str] = Field(None, description="Example input for this prompt")
    example_output: Optional[str] = Field(None, description="Example output for this prompt")
    performance_score: float = Field(default=5.0, ge=0, le=10, description="Initial score 0-10")
    agent_code: str = Field(default="RAFA", description="Agent that uses this prompt")
    version: int = Field(default=1, ge=1, description="Version number")
    is_active: bool = Field(default=True, description="Is this prompt active?")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Real Estate Instagram Caption - AIDA",
                "category": "caption",
                "vertical": "real_estate",
                "platform": "instagram",
                "technique": "AIDA",
                "source": "omega-tested",
                "prompt_text": "Crea un caption para Instagram que presente esta propiedad usando AIDA...",
                "performance_score": 8.5,
                "agent_code": "RAFA",
                "is_active": True
            }
        }


class PromptVaultUpdate(BaseModel):
    """Request model for updating an existing prompt"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    prompt_text: Optional[str] = Field(None, min_length=10)
    performance_score: Optional[float] = Field(None, ge=0, le=10)
    is_active: Optional[bool] = None
    technique: Optional[str] = None
    example_input: Optional[str] = None
    example_output: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "performance_score": 9.2,
                "is_active": True
            }
        }


class PromptVaultResponse(BaseModel):
    """Response model for prompt vault items"""
    id: str
    name: str
    category: str
    vertical: str
    platform: Optional[str]
    technique: str
    source: str
    prompt_text: str
    example_input: Optional[str]
    example_output: Optional[str]
    performance_score: float
    times_used: int
    engagement_avg: Optional[float]
    agent_code: str
    version: int
    is_active: bool
    created_at: datetime
    last_updated: Optional[datetime]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Real Estate Instagram Caption - AIDA",
                "category": "caption",
                "vertical": "real_estate",
                "platform": "instagram",
                "technique": "AIDA",
                "source": "omega-tested",
                "prompt_text": "Crea un caption...",
                "performance_score": 8.5,
                "times_used": 47,
                "engagement_avg": 0.038,
                "agent_code": "RAFA",
                "version": 1,
                "is_active": True,
                "created_at": "2026-02-28T10:00:00Z",
                "last_updated": "2026-02-28T15:30:00Z"
            }
        }


class PerformanceUpdateRequest(BaseModel):
    """Request model for updating prompt performance"""
    engagement_rate: float = Field(..., ge=0, le=1, description="Engagement rate (0.0 to 1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "engagement_rate": 0.045
            }
        }


class PromptVaultListResponse(BaseModel):
    """Response model for list of prompts"""
    prompts: list[PromptVaultResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "prompts": [],
                "total": 30
            }
        }
