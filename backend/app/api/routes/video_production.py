"""
Video Production API Routes
Endpoints for video scripting and production planning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.agents.video_production_agent import video_production_agent
from app.services.video_pipeline import VideoSpec, VideoScript

router = APIRouter(prefix="/video", tags=["video"])


# Request Models
class WriteScriptRequest(BaseModel):
    """Request for video script writing"""
    spec: VideoSpec = Field(..., description="Video specifications")
    brand_voice: str = Field(..., description="Brand voice guidelines")
    key_message: str = Field(..., description="Core message to communicate")


class ProductionPlanRequest(BaseModel):
    """Request for production plan creation"""
    spec: VideoSpec = Field(..., description="Video specifications")
    script: VideoScript = Field(..., description="Video script")


class OptimizeHookRequest(BaseModel):
    """Request for hook optimization"""
    platform: str = Field(..., description="Target platform")
    niche: str = Field(..., description="Content niche")
    content_topic: str = Field(..., description="Video topic")


class AdaptScriptRequest(BaseModel):
    """Request for script adaptation"""
    script: VideoScript = Field(..., description="Original script")
    target_platform: str = Field(..., description="Target platform")


class GenerateIdeasRequest(BaseModel):
    """Request for video idea generation"""
    niche: str = Field(..., description="Content niche")
    platform: str = Field(..., description="Target platform")
    content_pillars: List[str] = Field(..., description="Content pillars")


# Response Model
class VideoProductionAPIResponse(BaseModel):
    """Generic video production response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/write-script", response_model=VideoProductionAPIResponse)
async def write_script(
    request: WriteScriptRequest
) -> VideoProductionAPIResponse:
    """
    Write complete video script with powerful hook and CTA

    - **spec**: Video specifications (duration, platform, style)
    - **brand_voice**: Brand voice guidelines
    - **key_message**: Core message to communicate

    Returns complete script with hook, scenes, and call-to-action
    """
    try:
        result = await video_production_agent.execute({
            "type": "write_script",
            "spec": request.spec.model_dump(),
            "brand_voice": request.brand_voice,
            "key_message": request.key_message
        })

        return VideoProductionAPIResponse(
            success=True,
            data=result,
            message="Video script created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/production-plan", response_model=VideoProductionAPIResponse)
async def create_production_plan(
    request: ProductionPlanRequest
) -> VideoProductionAPIResponse:
    """
    Create detailed production plan with shot list

    - **spec**: Video specifications
    - **script**: Video script

    Returns production plan with shot list, text overlays, audio suggestions
    """
    try:
        result = await video_production_agent.execute({
            "type": "production_plan",
            "spec": request.spec.model_dump(),
            "script": request.script.model_dump()
        })

        return VideoProductionAPIResponse(
            success=True,
            data=result,
            message="Production plan created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-hook", response_model=VideoProductionAPIResponse)
async def optimize_hook(
    request: OptimizeHookRequest
) -> VideoProductionAPIResponse:
    """
    Generate 3 hook options for first 3 seconds

    - **platform**: Target platform
    - **niche**: Content niche
    - **content_topic**: Video topic

    Returns 3 optimized hook options
    """
    try:
        result = await video_production_agent.execute({
            "type": "optimize_hook",
            "platform": request.platform,
            "niche": request.niche,
            "content_topic": request.content_topic
        })

        return VideoProductionAPIResponse(
            success=True,
            data=result,
            message="Hook options generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adapt-platform", response_model=VideoProductionAPIResponse)
async def adapt_script_for_platform(
    request: AdaptScriptRequest
) -> VideoProductionAPIResponse:
    """
    Adapt existing script for another platform

    - **script**: Original video script
    - **target_platform**: Target platform for adaptation

    Returns adapted script optimized for target platform
    """
    try:
        result = await video_production_agent.execute({
            "type": "adapt_script",
            "script": request.script.model_dump(),
            "target_platform": request.target_platform
        })

        return VideoProductionAPIResponse(
            success=True,
            data=result,
            message=f"Script adapted for {request.target_platform}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-ideas", response_model=VideoProductionAPIResponse)
async def generate_video_ideas(
    request: GenerateIdeasRequest
) -> VideoProductionAPIResponse:
    """
    Generate 5 video ideas with title, hook and concept

    - **niche**: Content niche
    - **platform**: Target platform
    - **content_pillars**: Content pillars to cover

    Returns 5 video ideas with title, hook, and concept
    """
    try:
        result = await video_production_agent.execute({
            "type": "generate_ideas",
            "niche": request.niche,
            "platform": request.platform,
            "content_pillars": request.content_pillars
        })

        return VideoProductionAPIResponse(
            success=True,
            data={"ideas": result},
            message=f"Generated {len(result)} video ideas"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Video Production Agent status"""
    return video_production_agent.get_status()
