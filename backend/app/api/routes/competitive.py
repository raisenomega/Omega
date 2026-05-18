"""
Competitive Intelligence API Routes
Endpoints for competitor analysis and benchmarking
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.competitive_intelligence_agent import competitive_intelligence_agent
from app.services.competitor_analyzer import CompetitorProfile, ContentGapAnalysis

router = APIRouter(prefix="/competitive", tags=["competitive"])


# Request Models
class AnalyzeCompetitorRequest(BaseModel):
    """Request for competitor analysis"""
    competitor_data: Dict[str, Any] = Field(..., description="Competitor data")


class GenerateBenchmarkRequest(BaseModel):
    """Request for benchmark generation"""
    client_data: Dict[str, float] = Field(..., description="Client metrics")
    competitor_profile: CompetitorProfile = Field(..., description="Competitor profile")


class IdentifyGapsRequest(BaseModel):
    """Request for content gap analysis"""
    client_topics: List[str] = Field(..., description="Client content topics")
    competitor_topics: List[str] = Field(..., description="Competitor topics")
    niche: str = Field(..., description="Industry niche")


class RecommendStrategyRequest(BaseModel):
    """Request for strategy recommendations"""
    gap_analysis: ContentGapAnalysis = Field(..., description="Gap analysis")
    client_strengths: List[str] = Field(..., description="Client strengths")


# Response Model
class CompetitiveAPIResponse(BaseModel):
    """Generic competitive intelligence response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/analyze-competitor", response_model=CompetitiveAPIResponse)
async def analyze_competitor(
    request: AnalyzeCompetitorRequest
) -> CompetitiveAPIResponse:
    """
    Analyze competitor and generate profile
    
    - **competitor_data**: Competitor information
    
    Returns structured competitor profile
    """
    try:
        result = await competitive_intelligence_agent.execute({
            "type": "analyze_competitor",
            "competitor_data": request.competitor_data
        })
        
        return CompetitiveAPIResponse(
            success=True,
            data=result,
            message="Competitor analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-benchmark", response_model=CompetitiveAPIResponse)
async def generate_benchmark(
    request: GenerateBenchmarkRequest
) -> CompetitiveAPIResponse:
    """
    Generate benchmark comparison
    
    - **client_data**: Client metrics
    - **competitor_profile**: Competitor profile
    
    Returns benchmark report with performance gaps
    """
    try:
        result = await competitive_intelligence_agent.execute({
            "type": "generate_benchmark",
            "client_data": request.client_data,
            "competitor_profile": request.competitor_profile.model_dump()
        })
        
        return CompetitiveAPIResponse(
            success=True,
            data=result,
            message="Benchmark generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/identify-gaps", response_model=CompetitiveAPIResponse)
async def identify_gaps(
    request: IdentifyGapsRequest
) -> CompetitiveAPIResponse:
    """
    Identify content gaps
    
    - **client_topics**: Client content topics
    - **competitor_topics**: Competitor content topics
    - **niche**: Industry niche
    
    Returns content gap analysis with opportunities
    """
    try:
        result = await competitive_intelligence_agent.execute({
            "type": "identify_gaps",
            "client_topics": request.client_topics,
            "competitor_topics": request.competitor_topics,
            "niche": request.niche
        })
        
        return CompetitiveAPIResponse(
            success=True,
            data=result,
            message="Content gaps identified successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-strategy", response_model=CompetitiveAPIResponse)
async def recommend_strategy(
    request: RecommendStrategyRequest
) -> CompetitiveAPIResponse:
    """
    Generate strategic recommendations
    
    - **gap_analysis**: Content gap analysis
    - **client_strengths**: Client strengths
    
    Returns actionable strategic recommendations
    """
    try:
        result = await competitive_intelligence_agent.execute({
            "type": "recommend_strategy",
            "gap_analysis": request.gap_analysis.model_dump(),
            "client_strengths": request.client_strengths
        })
        
        return CompetitiveAPIResponse(
            success=True,
            data={"recommendations": result},
            message="Strategy recommendations generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Competitive Intelligence Agent status"""
    return competitive_intelligence_agent.get_status()
