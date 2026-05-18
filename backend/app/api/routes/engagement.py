"""
Engagement API Routes
Endpoints for user interaction and community management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.engagement_agent import engagement_agent

router = APIRouter(prefix="/engagement", tags=["engagement"])


# Request Models
class RespondCommentRequest(BaseModel):
    """Request for comment response"""
    comment: str = Field(..., description="Comment text")
    platform: str = Field(default="instagram", description="Social platform")
    brand_voice: str = Field(default="friendly", description="Brand voice tone")
    post_context: Dict[str, Any] = Field(default={}, description="Post context")


class HandleDMRequest(BaseModel):
    """Request for DM handling"""
    message: str = Field(..., description="DM message")
    platform: str = Field(..., description="Social platform")
    conversation_history: List[Dict[str, Any]] = Field(
        default=[],
        description="Previous messages"
    )


class AnalyzeCommentRequest(BaseModel):
    """Request for comment analysis"""
    comment: str = Field(..., description="Comment to analyze")


class DetectCrisisRequest(BaseModel):
    """Request for crisis detection"""
    comments: List[str] = Field(..., description="List of comments")
    threshold: float = Field(
        default=0.3,
        description="Negative ratio threshold for crisis"
    )


class BulkAnalyzeRequest(BaseModel):
    """Request for bulk comment analysis"""
    comments: List[str] = Field(..., description="Comments to analyze")
    platform: str = Field(default="instagram", description="Platform")


# Response Model
class EngagementAPIResponse(BaseModel):
    """Generic engagement response"""
    success: bool
    data: Dict[str, Any]
    message: Optional[str] = None


@router.post("/respond-comment", response_model=EngagementAPIResponse)
async def respond_comment(
    request: RespondCommentRequest
) -> EngagementAPIResponse:
    """
    Generate response to a comment
    
    - **comment**: Comment text to respond to
    - **platform**: Social media platform
    - **brand_voice**: Tone (friendly/professional/casual/formal)
    - **post_context**: Additional context about the post
    
    Returns AI-generated response with alternatives
    """
    try:
        result = await engagement_agent.execute({
            "type": "respond_comment",
            "comment": request.comment,
            "platform": request.platform,
            "brand_voice": request.brand_voice,
            "context": request.post_context
        })
        
        return EngagementAPIResponse(
            success=True,
            data=result,
            message="Response generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/handle-dm", response_model=EngagementAPIResponse)
async def handle_dm(request: HandleDMRequest) -> EngagementAPIResponse:
    """
    Handle direct message
    
    - **message**: DM message text
    - **platform**: Social media platform
    - **conversation_history**: Previous conversation messages
    
    Returns contextual response based on conversation history
    """
    try:
        result = await engagement_agent.execute({
            "type": "handle_dm",
            "message": request.message,
            "platform": request.platform,
            "conversation_history": request.conversation_history
        })
        
        return EngagementAPIResponse(
            success=True,
            data=result,
            message="DM response generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-comment", response_model=EngagementAPIResponse)
async def analyze_comment(
    request: AnalyzeCommentRequest
) -> EngagementAPIResponse:
    """
    Analyze comment sentiment and intent
    
    - **comment**: Comment text to analyze
    
    Returns sentiment, intent, keywords, and urgency score
    """
    try:
        result = await engagement_agent.execute({
            "type": "analyze",
            "comment": request.comment
        })
        
        return EngagementAPIResponse(
            success=True,
            data=result,
            message="Comment analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-crisis", response_model=EngagementAPIResponse)
async def detect_crisis(request: DetectCrisisRequest) -> EngagementAPIResponse:
    """
    Detect potential PR crisis
    
    - **comments**: List of comments to analyze
    - **threshold**: Negative ratio threshold (default 0.3)
    
    Returns crisis assessment with severity and recommended actions
    """
    try:
        result = await engagement_agent.execute({
            "type": "detect_crisis",
            "comments": request.comments
        })
        
        return EngagementAPIResponse(
            success=True,
            data=result,
            message="Crisis detection completed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-analyze", response_model=EngagementAPIResponse)
async def bulk_analyze(request: BulkAnalyzeRequest) -> EngagementAPIResponse:
    """
    Analyze multiple comments in bulk
    
    - **comments**: List of comments to analyze
    - **platform**: Social media platform
    
    Returns analysis for each comment
    """
    try:
        results = []
        for comment in request.comments:
            analysis = await engagement_agent.execute({
                "type": "analyze",
                "comment": comment
            })
            results.append(analysis)
        
        return EngagementAPIResponse(
            success=True,
            data={
                "analyses": results,
                "total_analyzed": len(results)
            },
            message=f"Analyzed {len(results)} comments successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Engagement Agent status"""
    return engagement_agent.get_status()
