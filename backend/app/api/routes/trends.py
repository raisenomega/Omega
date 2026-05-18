"""
Trends API Routes
Endpoints for trend detection and virality prediction
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.trend_hunter_agent import trend_hunter_agent
from app.services.trend_processor import TrendingTopic, TrendOpportunity

router = APIRouter(prefix="/trends", tags=["trends"])


# Request Models
class AnalyzeTrendsRequest(BaseModel):
    """Request for trend analysis"""
    platform_data: Dict[str, List[str]] = Field(..., description="Platform trending data")
    client_niche: str = Field(..., description="Client niche/industry")


class PredictViralityRequest(BaseModel):
    """Request for virality prediction"""
    content_description: str = Field(..., description="Content description")
    platform: str = Field(..., description="Target platform")
    target_audience: str = Field(..., description="Target audience")


class FindOpportunitiesRequest(BaseModel):
    """Request for opportunity finding"""
    trends: List[TrendingTopic] = Field(..., description="List of trends")
    client_niche: str = Field(..., description="Client niche")
    brand_profile: Dict[str, str] = Field(..., description="Brand profile")


class GenerateContentRequest(BaseModel):
    """Request for trend content generation"""
    opportunity: TrendOpportunity = Field(..., description="Trend opportunity")
    platform: str = Field(..., description="Target platform")


# Response Model
class TrendsAPIResponse(BaseModel):
    """Generic trends response"""
    success: bool
    data: dict | list
    message: Optional[str] = None


@router.post("/analyze", response_model=TrendsAPIResponse)
async def analyze_trends(
    request: AnalyzeTrendsRequest
) -> TrendsAPIResponse:
    """
    Analyze trends from platform data
    
    - **platform_data**: Trending topics by platform
    - **client_niche**: Client industry/niche
    
    Returns list of relevant trending topics
    """
    try:
        result = await trend_hunter_agent.execute({
            "type": "analyze_trends",
            "platform_data": request.platform_data,
            "client_niche": request.client_niche
        })
        
        return TrendsAPIResponse(
            success=True,
            data=result,
            message="Trends analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-virality", response_model=TrendsAPIResponse)
async def predict_virality(
    request: PredictViralityRequest
) -> TrendsAPIResponse:
    """
    Predict virality potential
    
    - **content_description**: Description of content
    - **platform**: Target platform
    - **target_audience**: Target audience
    
    Returns virality prediction with success factors
    """
    try:
        result = await trend_hunter_agent.execute({
            "type": "predict_virality",
            "content_description": request.content_description,
            "platform": request.platform,
            "target_audience": request.target_audience
        })
        
        return TrendsAPIResponse(
            success=True,
            data=result,
            message="Virality predicted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-opportunities", response_model=TrendsAPIResponse)
async def find_opportunities(
    request: FindOpportunitiesRequest
) -> TrendsAPIResponse:
    """
    Find trend opportunities
    
    - **trends**: List of trending topics
    - **client_niche**: Client niche
    - **brand_profile**: Brand profile
    
    Returns actionable trend opportunities
    """
    try:
        result = await trend_hunter_agent.execute({
            "type": "find_opportunities",
            "trends": [t.model_dump() for t in request.trends],
            "client_niche": request.client_niche,
            "brand_profile": request.brand_profile
        })
        
        return TrendsAPIResponse(
            success=True,
            data=result,
            message="Opportunities identified successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-content", response_model=TrendsAPIResponse)
async def generate_content(
    request: GenerateContentRequest
) -> TrendsAPIResponse:
    """
    Generate trend-based content
    
    - **opportunity**: Trend opportunity
    - **platform**: Target platform
    
    Returns specific content idea for trend
    """
    try:
        result = await trend_hunter_agent.execute({
            "type": "generate_content",
            "opportunity": request.opportunity.model_dump(),
            "platform": request.platform
        })
        
        return TrendsAPIResponse(
            success=True,
            data=result,
            message="Content generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Trend Hunter Agent status"""
    return trend_hunter_agent.get_status()
