"""
Crisis Management API Routes
Endpoints for crisis detection, response and recovery
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.crisis_manager_agent import crisis_manager_agent

router = APIRouter(prefix="/crisis", tags=["crisis"])


# Request Models
class AssessCrisisRequest(BaseModel):
    """Request for crisis assessment"""
    platform: str = Field(..., description="Platform where crisis occurred")
    negative_comment_percentage: float = Field(..., description="Percentage of negative comments")
    complaint_velocity: int = Field(..., description="Complaints per hour")
    sentiment_drop: float = Field(default=0.0, description="Drop from sentiment baseline")
    reach_of_negative_content: int = Field(..., description="Reach of negative content")
    media_involvement: bool = Field(default=False, description="Media coverage involved")
    influencer_involvement: bool = Field(default=False, description="Influencer involvement")


class ResponseStrategyRequest(BaseModel):
    """Request for response strategy"""
    assessment: Dict[str, Any] = Field(..., description="Crisis assessment data")
    brand_profile: Dict[str, str] = Field(..., description="Brand profile")


class DraftStatementRequest(BaseModel):
    """Request for official statement"""
    assessment: Dict[str, Any] = Field(..., description="Crisis assessment data")
    brand_voice: str = Field(..., description="Brand voice tone")
    brand_name: str = Field(..., description="Brand name")


class RecoveryPlanRequest(BaseModel):
    """Request for recovery plan"""
    assessment: Dict[str, Any] = Field(..., description="Crisis assessment data")


class ImmediateActionsRequest(BaseModel):
    """Request for immediate actions"""
    crisis_level: Dict[str, Any] = Field(..., description="Crisis level data")


# Response Model
class CrisisAPIResponse(BaseModel):
    """Generic crisis management response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/assess", response_model=CrisisAPIResponse)
async def assess_crisis(request: AssessCrisisRequest) -> CrisisAPIResponse:
    """
    Assess crisis severity and impact

    - **platform**: Platform where crisis occurred
    - **negative_comment_percentage**: Percentage of negative comments
    - **complaint_velocity**: Complaints per hour
    - **reach_of_negative_content**: Reach of negative content
    - **media_involvement**: Whether media is covering the crisis
    - **influencer_involvement**: Whether influencers are involved

    Returns crisis level, impact assessment, and recommended actions
    """
    try:
        result = await crisis_manager_agent.execute({
            "type": "assess",
            "signals": {
                "platform": request.platform,
                "negative_comment_percentage": request.negative_comment_percentage,
                "complaint_velocity": request.complaint_velocity,
                "sentiment_drop": request.sentiment_drop,
                "reach_of_negative_content": request.reach_of_negative_content,
                "media_involvement": request.media_involvement,
                "influencer_involvement": request.influencer_involvement
            }
        })

        return CrisisAPIResponse(
            success=True,
            data=result,
            message="Crisis assessed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response-strategy", response_model=CrisisAPIResponse)
async def generate_response_strategy(
    request: ResponseStrategyRequest
) -> CrisisAPIResponse:
    """
    Generate crisis response strategy

    - **assessment**: Crisis assessment data
    - **brand_profile**: Brand profile information

    Returns comprehensive response strategy
    """
    try:
        result = await crisis_manager_agent.execute({
            "type": "response_strategy",
            "assessment": request.assessment,
            "brand_profile": request.brand_profile
        })

        return CrisisAPIResponse(
            success=True,
            data=result,
            message="Response strategy generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/draft-statement", response_model=CrisisAPIResponse)
async def draft_statement(request: DraftStatementRequest) -> CrisisAPIResponse:
    """
    Draft official crisis statement

    - **assessment**: Crisis assessment data
    - **brand_voice**: Brand voice tone
    - **brand_name**: Brand name

    Returns professionally crafted crisis statement
    """
    try:
        result = await crisis_manager_agent.execute({
            "type": "draft_statement",
            "assessment": request.assessment,
            "brand_voice": request.brand_voice,
            "brand_name": request.brand_name
        })

        return CrisisAPIResponse(
            success=True,
            data={"statement": result},
            message="Statement drafted successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recovery-plan", response_model=CrisisAPIResponse)
async def create_recovery_plan(
    request: RecoveryPlanRequest
) -> CrisisAPIResponse:
    """
    Create step-by-step recovery plan

    - **assessment**: Crisis assessment data

    Returns detailed recovery roadmap
    """
    try:
        result = await crisis_manager_agent.execute({
            "type": "recovery_plan",
            "assessment": request.assessment
        })

        return CrisisAPIResponse(
            success=True,
            data={"recovery_steps": result},
            message="Recovery plan created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/immediate-actions", response_model=CrisisAPIResponse)
async def recommend_immediate_actions(
    request: ImmediateActionsRequest
) -> CrisisAPIResponse:
    """
    Get immediate actions for crisis (next 60 minutes)

    - **crisis_level**: Crisis level data

    Returns prioritized action list
    """
    try:
        result = await crisis_manager_agent.execute({
            "type": "immediate_actions",
            "crisis_level": request.crisis_level
        })

        return CrisisAPIResponse(
            success=True,
            data={"actions": result},
            message="Immediate actions recommended"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Crisis Manager Agent status"""
    return crisis_manager_agent.get_status()
