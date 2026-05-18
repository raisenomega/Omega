"""
Strategy API Routes
Endpoints for content strategy and planning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.agents.strategy_agent import strategy_agent

router = APIRouter(prefix="/strategy", tags=["strategy"])


# Request/Response Models
class CreateCalendarRequest(BaseModel):
    """Request model for calendar creation"""
    duration_days: int = Field(default=30, description="Calendar duration in days")
    platforms: List[str] = Field(default=["instagram"], description="Target platforms")
    goals: List[str] = Field(default=[], description="Strategic goals")


class OptimizeTimingRequest(BaseModel):
    """Request model for timing optimization"""
    platform: str = Field(..., description="Social media platform")
    timezone: str = Field(default="UTC", description="Timezone")
    audience_data: Dict[str, Any] = Field(default={}, description="Audience insights")


class ContentMixRequest(BaseModel):
    """Request model for content mix optimization"""
    current_mix: Dict[str, float] = Field(..., description="Current content percentages")
    goals: List[str] = Field(default=[], description="Strategic goals")
    industry: str = Field(default="general", description="Industry vertical")


class StrategyAnalysisRequest(BaseModel):
    """Request model for strategy analysis"""
    context: Dict[str, Any] = Field(..., description="Business context")
    goals: List[str] = Field(..., description="Strategic goals")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Constraints")


class StrategyResponse(BaseModel):
    """Generic strategy response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/create-calendar", response_model=StrategyResponse)
async def create_calendar(request: CreateCalendarRequest) -> StrategyResponse:
    """
    Create content calendar
    
    - **duration_days**: How many days to plan
    - **platforms**: Which platforms to include
    - **goals**: Strategic objectives
    """
    try:
        result = await strategy_agent.execute({
            "type": "calendar",
            "duration_days": request.duration_days,
            "platforms": request.platforms,
            "goals": request.goals
        })
        
        return StrategyResponse(
            success=True,
            data=result,
            message="Calendar created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-timing", response_model=StrategyResponse)
async def optimize_timing(request: OptimizeTimingRequest) -> StrategyResponse:
    """
    Optimize posting times
    
    - **platform**: Target platform
    - **timezone**: User timezone
    - **audience_data**: Audience insights
    """
    try:
        result = await strategy_agent.execute({
            "type": "timing",
            "platform": request.platform,
            "timezone": request.timezone,
            "audience_data": request.audience_data
        })
        
        return StrategyResponse(
            success=True,
            data=result,
            message="Timing optimized successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-content-mix", response_model=StrategyResponse)
async def optimize_content_mix(request: ContentMixRequest) -> StrategyResponse:
    """
    Optimize content mix
    
    - **current_mix**: Current content distribution
    - **goals**: Strategic goals
    - **industry**: Industry vertical
    """
    try:
        result = await strategy_agent.execute({
            "type": "mix",
            "current_mix": request.current_mix,
            "goals": request.goals,
            "industry": request.industry
        })
        
        return StrategyResponse(
            success=True,
            data=result,
            message="Content mix optimized successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-strategy", response_model=StrategyResponse)
async def analyze_strategy(request: StrategyAnalysisRequest) -> StrategyResponse:
    """
    Comprehensive strategy analysis
    
    - **context**: Business context and current state
    - **goals**: Strategic objectives
    - **constraints**: Budget, time, resource limits
    """
    try:
        result = await strategy_agent.execute({
            "type": "analysis",
            "context": request.context,
            "goals": request.goals,
            "constraints": request.constraints
        })
        
        return StrategyResponse(
            success=True,
            data=result,
            message="Strategy analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Strategy Agent status"""
    return strategy_agent.get_status()
