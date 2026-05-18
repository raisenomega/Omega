"""
Brand Voice API Routes
Endpoints for brand consistency and validation
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from app.agents.brand_voice_agent import brand_voice_agent
from app.services.brand_analyzer import BrandProfile

router = APIRouter(prefix="/brand-voice", tags=["brand-voice"])


# Request Models
class ValidateContentRequest(BaseModel):
    """Request for content validation"""
    content: str = Field(..., description="Content to validate")
    brand_profile: BrandProfile = Field(..., description="Brand profile")


class ImproveContentRequest(BaseModel):
    """Request for content improvement"""
    content: str = Field(..., description="Content to improve")
    brand_profile: BrandProfile = Field(..., description="Brand profile")


class CreateProfileRequest(BaseModel):
    """Request for brand profile creation"""
    client_name: str = Field(..., description="Client name")
    brand_description: str = Field(..., description="Brand description")
    sample_posts: List[str] = Field(..., description="Sample posts")


class AdaptPlatformRequest(BaseModel):
    """Request for platform adaptation"""
    content: str = Field(..., description="Content to adapt")
    platform: str = Field(..., description="Target platform")
    brand_profile: BrandProfile = Field(..., description="Brand profile")


# Response Model
class BrandVoiceAPIResponse(BaseModel):
    """Generic brand voice response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/validate-content", response_model=BrandVoiceAPIResponse)
async def validate_content(
    request: ValidateContentRequest
) -> BrandVoiceAPIResponse:
    """
    Validate content against brand profile
    
    - **content**: Content to validate
    - **brand_profile**: Brand voice profile
    
    Returns validation result with compliance score and violations
    """
    try:
        result = await brand_voice_agent.execute({
            "type": "validate",
            "content": request.content,
            "brand_profile": request.brand_profile.model_dump()
        })
        
        return BrandVoiceAPIResponse(
            success=True,
            data=result,
            message="Content validated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-content", response_model=BrandVoiceAPIResponse)
async def improve_content(
    request: ImproveContentRequest
) -> BrandVoiceAPIResponse:
    """
    Improve content to align with brand voice
    
    - **content**: Content to improve
    - **brand_profile**: Brand voice profile
    
    Returns improved content with changes made
    """
    try:
        result = await brand_voice_agent.execute({
            "type": "improve",
            "content": request.content,
            "brand_profile": request.brand_profile.model_dump()
        })
        
        return BrandVoiceAPIResponse(
            success=True,
            data=result,
            message="Content improved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-profile", response_model=BrandVoiceAPIResponse)
async def create_profile(
    request: CreateProfileRequest
) -> BrandVoiceAPIResponse:
    """
    Create brand profile from samples
    
    - **client_name**: Client name
    - **brand_description**: Brand description
    - **sample_posts**: Sample posts for analysis
    
    Returns generated brand profile
    """
    try:
        result = await brand_voice_agent.execute({
            "type": "create_profile",
            "client_name": request.client_name,
            "brand_description": request.brand_description,
            "sample_posts": request.sample_posts
        })
        
        return BrandVoiceAPIResponse(
            success=True,
            data=result,
            message="Brand profile created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adapt-platform", response_model=BrandVoiceAPIResponse)
async def adapt_platform(
    request: AdaptPlatformRequest
) -> BrandVoiceAPIResponse:
    """
    Adapt content for specific platform
    
    - **content**: Content to adapt
    - **platform**: Target platform (instagram/facebook/tiktok/twitter/linkedin)
    - **brand_profile**: Brand voice profile
    
    Returns platform-adapted content
    """
    try:
        result = await brand_voice_agent.execute({
            "type": "adapt_platform",
            "content": request.content,
            "platform": request.platform,
            "brand_profile": request.brand_profile.model_dump()
        })
        
        return BrandVoiceAPIResponse(
            success=True,
            data=result,
            message=f"Content adapted for {request.platform}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Brand Voice Agent status"""
    return brand_voice_agent.get_status()
