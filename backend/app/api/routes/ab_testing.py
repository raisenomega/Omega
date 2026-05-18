"""
A/B Testing API Routes
Endpoints for scientific experimentation and optimization
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from app.agents.ab_testing_agent import ab_testing_agent
from app.services.experiment_engine import Experiment, ABTestResult

router = APIRouter(prefix="/ab-testing", tags=["ab-testing"])


# Request Models
class DesignExperimentRequest(BaseModel):
    """Request for experiment design"""
    hypothesis: str = Field(..., description="Test hypothesis")
    variable: str = Field(..., description="Variable to test")
    base_content: dict[str, str] = Field(..., description="Base content")
    platform: str = Field(..., description="Target platform")


class CreateVariantsRequest(BaseModel):
    """Request for variant creation"""
    base_content: dict[str, str] = Field(..., description="Base content")
    variable: str = Field(..., description="Variable to test")
    client_niche: str = Field(..., description="Client niche")


class AnalyzeResultsRequest(BaseModel):
    """Request for results analysis"""
    experiment: Experiment = Field(..., description="Experiment with data")


class GenerateInsightsRequest(BaseModel):
    """Request for insight generation"""
    results: List[ABTestResult] = Field(..., description="Test results")
    client_id: str = Field(..., description="Client ID")


class RecommendNextRequest(BaseModel):
    """Request for next test recommendation"""
    completed_experiments: List[Experiment] = Field(..., description="Completed experiments")
    client_goals: List[str] = Field(..., description="Client goals")


# Response Model
class ABTestingAPIResponse(BaseModel):
    """Generic A/B testing response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/design-experiment", response_model=ABTestingAPIResponse)
async def design_experiment(
    request: DesignExperimentRequest
) -> ABTestingAPIResponse:
    """
    Design scientific experiment with clear variants

    - **hypothesis**: Test hypothesis
    - **variable**: Variable to test (caption/image/posting_time/hashtags/cta/hook)
    - **base_content**: Base content to test against
    - **platform**: Target platform

    Returns experiment design with target sample size
    """
    try:
        result = await ab_testing_agent.execute({
            "type": "design_experiment",
            "hypothesis": request.hypothesis,
            "variable": request.variable,
            "base_content": request.base_content,
            "platform": request.platform
        })

        return ABTestingAPIResponse(
            success=True,
            data=result,
            message="Experiment designed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-variants", response_model=ABTestingAPIResponse)
async def create_variants(
    request: CreateVariantsRequest
) -> ABTestingAPIResponse:
    """
    Create A and B variants for testing

    - **base_content**: Base content
    - **variable**: Variable to test
    - **client_niche**: Client niche for context

    Returns variant A (control) and variant B (test)
    """
    try:
        result = await ab_testing_agent.execute({
            "type": "create_variants",
            "base_content": request.base_content,
            "variable": request.variable,
            "client_niche": request.client_niche
        })

        return ABTestingAPIResponse(
            success=True,
            data={"variants": result},
            message="Variants created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-results", response_model=ABTestingAPIResponse)
async def analyze_results(
    request: AnalyzeResultsRequest
) -> ABTestingAPIResponse:
    """
    Analyze experiment results with statistical significance

    - **experiment**: Experiment with performance data

    Returns statistical analysis with winner, significance, and insights
    """
    try:
        result = await ab_testing_agent.execute({
            "type": "analyze_results",
            "experiment": request.experiment.model_dump()
        })

        return ABTestingAPIResponse(
            success=True,
            data=result,
            message="Results analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-insights", response_model=ABTestingAPIResponse)
async def generate_insights(
    request: GenerateInsightsRequest
) -> ABTestingAPIResponse:
    """
    Generate cumulative insights from multiple experiments

    - **results**: List of test results
    - **client_id**: Client identifier

    Returns strategic insights across all tests
    """
    try:
        result = await ab_testing_agent.execute({
            "type": "generate_insights",
            "results": [r.model_dump() for r in request.results],
            "client_id": request.client_id
        })

        return ABTestingAPIResponse(
            success=True,
            data={"insights": result},
            message=f"Generated {len(result)} insights"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-next", response_model=ABTestingAPIResponse)
async def recommend_next_test(
    request: RecommendNextRequest
) -> ABTestingAPIResponse:
    """
    Recommend next experiment based on history

    - **completed_experiments**: List of completed experiments
    - **client_goals**: Client goals and objectives

    Returns recommendation for next test with reasoning
    """
    try:
        result = await ab_testing_agent.execute({
            "type": "recommend_next",
            "completed_experiments": [e.model_dump() for e in request.completed_experiments],
            "client_goals": request.client_goals
        })

        return ABTestingAPIResponse(
            success=True,
            data=result,
            message="Next test recommended successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get A/B Testing Agent status"""
    return ab_testing_agent.get_status()
