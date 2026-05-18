"""
Content Generation API Routes
Endpoints for AI-powered content creation
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.agents.content_creator import content_creator_agent
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.repositories.context_repository import context_repository

router = APIRouter(prefix="/content", tags=["content"])


async def get_client_brief(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    FastAPI dependency: injects client AI brief into content endpoints.
    Returns None if no auth or no context (graceful degradation).
    """
    try:
        client_id = await get_current_user_id(authorization)
        return await context_repository.get_context_for_generation(client_id)
    except Exception:
        return None  # Sin contexto → genera igual, sin error


# Request/Response Models
class CaptionRequest(BaseModel):
    """Request model for caption generation"""
    topic: str = Field(..., description="Content topic")
    platform: str = Field(default="instagram", description="Target platform")
    tone: str = Field(default="professional", description="Content tone")


class ImageRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Image description")
    size: str = Field(default="1024x1024", description="Image size")
    quality: str = Field(default="standard", description="Image quality")


class HashtagRequest(BaseModel):
    """Request model for hashtag generation"""
    topic: str = Field(..., description="Content topic")
    count: int = Field(default=10, description="Number of hashtags")
    platform: str = Field(default="instagram", description="Target platform")


class VideoScriptRequest(BaseModel):
    """Request model for video script generation"""
    topic: str = Field(..., description="Video topic")
    duration: int = Field(default=30, description="Video duration in seconds")
    style: str = Field(default="professional", description="Video style")


class ContentResponse(BaseModel):
    """Generic content response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/generate-caption", response_model=ContentResponse)
async def generate_caption(
    request: CaptionRequest,
    brief: Optional[str] = Depends(get_client_brief)
) -> ContentResponse:
    """
    Generate social media caption

    - **topic**: What the post is about
    - **platform**: Target social media platform
    - **tone**: Desired tone (professional, casual, excited, etc.)
    """
    try:
        result = await content_creator_agent.execute({
            "type": "caption",
            "topic": request.topic,
            "platform": request.platform,
            "tone": request.tone,
            "brief": brief
        })
        
        return ContentResponse(
            success=True,
            data=result,
            message="Caption generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-image", response_model=ContentResponse)
async def generate_image(
    request: ImageRequest,
    brief: Optional[str] = Depends(get_client_brief)
) -> ContentResponse:
    """
    Generate image with DALL-E 3

    - **prompt**: Description of the image to generate
    - **size**: Image dimensions (1024x1024, 1024x1792, 1792x1024)
    - **quality**: Image quality (standard, hd)
    """
    try:
        result = await content_creator_agent.execute({
            "type": "image",
            "prompt": request.prompt,
            "size": request.size,
            "quality": request.quality,
            "brief": brief
        })
        
        return ContentResponse(
            success=True,
            data=result,
            message="Image generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-hashtags", response_model=ContentResponse)
async def generate_hashtags(
    request: HashtagRequest,
    brief: Optional[str] = Depends(get_client_brief)
) -> ContentResponse:
    """
    Generate relevant hashtags

    - **topic**: Content topic
    - **count**: Number of hashtags to generate
    - **platform**: Target platform
    """
    try:
        result = await content_creator_agent.execute({
            "type": "hashtags",
            "topic": request.topic,
            "count": request.count,
            "platform": request.platform,
            "brief": brief
        })
        
        return ContentResponse(
            success=True,
            data=result,
            message="Hashtags generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video-script", response_model=ContentResponse)
async def generate_video_script(
    request: VideoScriptRequest,
    brief: Optional[str] = Depends(get_client_brief)
) -> ContentResponse:
    """
    Generate video script

    - **topic**: Video topic
    - **duration**: Video duration in seconds
    - **style**: Video style (professional, casual, energetic, etc.)
    """
    try:
        result = await content_creator_agent.execute({
            "type": "video_script",
            "topic": request.topic,
            "duration": request.duration,
            "style": request.style,
            "brief": brief
        })
        
        return ContentResponse(
            success=True,
            data=result,
            message="Video script generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Content Creator Agent status"""
    return content_creator_agent.get_status()
