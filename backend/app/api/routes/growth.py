"""
Growth Hacker API Routes
Endpoints for growth optimization and experiments
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.growth_hacker_agent import growth_hacker_agent

router = APIRouter(prefix="/growth", tags=["growth"])


# Request Models
class IdentifyOpportunitiesRequest(BaseModel):
    """Request for opportunity identification"""
    account_data: Dict[str, Any] = Field(..., description="Account metrics and data")
    niche: str = Field(..., description="Industry/niche")
    platform: str = Field(..., description="Platform name")


class DesignExperimentRequest(BaseModel):
    """Request for experiment design"""
    opportunity: Dict[str, Any] = Field(..., description="Growth opportunity")


class AnalyzeTrajectoryRequest(BaseModel):
    """Request for growth trajectory analysis"""
    historical_data: List[Dict[str, float]] = Field(..., description="Historical metrics")
    industry_benchmarks: Dict[str, float] = Field(..., description="Industry benchmarks")


class QuickWinsRequest(BaseModel):
    """Request for quick wins"""
    account_data: Dict[str, Any] = Field(..., description="Account data")
    platform: str = Field(..., description="Platform name")


# Response Model
class GrowthAPIResponse(BaseModel):
    """Generic growth response"""
    success: bool
    data: dict | list
    message: str | None = None


@router.post("/identify-opportunities", response_model=GrowthAPIResponse)
async def identify_opportunities(
    request: IdentifyOpportunitiesRequest
) -> GrowthAPIResponse:
    """
    Identify top growth opportunities

    - **account_data**: Account metrics and data
    - **niche**: Industry or niche
    - **platform**: Social media platform

    Returns ranked list of growth opportunities with ROI estimates
    """
    try:
        result = await growth_hacker_agent.execute({
            "type": "identify_opportunities",
            "account_data": request.account_data,
            "niche": request.niche,
            "platform": request.platform
        })

        return GrowthAPIResponse(
            success=True,
            data=result,
            message="Opportunities identified successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/design-experiment", response_model=GrowthAPIResponse)
async def design_experiment(
    request: DesignExperimentRequest
) -> GrowthAPIResponse:
    """
    Design scientific growth experiment

    - **opportunity**: Growth opportunity to test

    Returns experiment design with hypothesis, variables, and success metrics
    """
    try:
        result = await growth_hacker_agent.execute({
            "type": "design_experiment",
            "opportunity": request.opportunity
        })

        return GrowthAPIResponse(
            success=True,
            data=result,
            message="Experiment designed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-trajectory", response_model=GrowthAPIResponse)
async def analyze_trajectory(
    request: AnalyzeTrajectoryRequest
) -> GrowthAPIResponse:
    """
    Analyze growth trajectory and generate report

    - **historical_data**: Historical metrics
    - **industry_benchmarks**: Industry benchmark data

    Returns comprehensive growth report with gaps and recommendations
    """
    try:
        result = await growth_hacker_agent.execute({
            "type": "analyze_trajectory",
            "historical_data": request.historical_data,
            "industry_benchmarks": request.industry_benchmarks
        })

        return GrowthAPIResponse(
            success=True,
            data=result,
            message="Growth trajectory analyzed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-wins", response_model=GrowthAPIResponse)
async def generate_quick_wins(
    request: QuickWinsRequest
) -> GrowthAPIResponse:
    """
    Generate quick wins (<48h implementation)

    - **account_data**: Account data
    - **platform**: Platform name

    Returns 5 actionable quick wins for immediate implementation
    """
    try:
        result = await growth_hacker_agent.execute({
            "type": "quick_wins",
            "account_data": request.account_data,
            "platform": request.platform
        })

        return GrowthAPIResponse(
            success=True,
            data={"quick_wins": result},
            message="Quick wins generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Growth Hacker Agent status"""
    return growth_hacker_agent.get_status()
