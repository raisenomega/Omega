"""
Analytics API Routes
Endpoints for data analysis and insights
"""
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.agents.analytics_agent import analytics_agent
from app.api.routes.analytics.handlers.get_dashboard import handle_get_dashboard
from app.api.routes.auth.auth_utils import get_current_user, require_superadmin
from app.api.routes.calendar_v3._access import resolve_client_or_403

router = APIRouter(prefix="/analytics", tags=["analytics"])


# Request/Response Models
class AnalyzeMetricsRequest(BaseModel):
    """Request model for metrics analysis"""
    data: Dict[str, Any] = Field(..., description="Metrics data")


class DetectPatternsRequest(BaseModel):
    """Request model for pattern detection"""
    historical_data: List[Dict[str, Any]] = Field(..., description="Historical data points")


class GenerateInsightsRequest(BaseModel):
    """Request model for insights generation"""
    metrics: Dict[str, Any] = Field(..., description="Metrics to analyze")


class ForecastRequest(BaseModel):
    """Request model for performance forecasting"""
    historical_data: List[Dict[str, Any]] = Field(..., description="Historical data")
    days_ahead: int = Field(default=7, description="Days to forecast")


class DashboardRequest(BaseModel):
    """Request model for dashboard data"""
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Data filters")


class AnalyticsResponse(BaseModel):
    """Generic analytics response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.post("/analyze-metrics", response_model=AnalyticsResponse)
async def analyze_metrics(
    request: AnalyzeMetricsRequest,
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Analyze social media metrics
    
    - **data**: Metrics including likes, comments, shares, followers, impressions
    
    Returns engagement rate, reach percentage, and AI-generated insights
    """
    await get_current_user(authorization)  # IDOR fix · auth requerida (anti-abuso de cómputo)
    try:
        result = await analytics_agent.execute({
            "type": "analyze",
            "data": request.data
        })
        
        return AnalyticsResponse(
            success=True,
            data=result,
            message="Metrics analyzed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-patterns", response_model=AnalyticsResponse)
async def detect_patterns(
    request: DetectPatternsRequest,
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Detect patterns in historical data
    
    - **historical_data**: List of data points with timestamps and values
    
    Returns moving averages, anomalies, growth trends, and AI analysis
    """
    await get_current_user(authorization)  # IDOR fix · auth requerida (anti-abuso de cómputo)
    try:
        result = await analytics_agent.execute({
            "type": "patterns",
            "historical_data": request.historical_data
        })
        
        return AnalyticsResponse(
            success=True,
            data=result,
            message="Patterns detected successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-insights", response_model=AnalyticsResponse)
async def generate_insights(
    request: GenerateInsightsRequest,
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Generate actionable insights from metrics
    
    - **metrics**: Dictionary of metrics to analyze
    
    Returns AI-generated insights with observations and action items
    """
    await get_current_user(authorization)  # IDOR fix · auth requerida (anti-abuso de cómputo)
    try:
        result = await analytics_agent.execute({
            "type": "insights",
            "metrics": request.metrics
        })
        
        return AnalyticsResponse(
            success=True,
            data=result,
            message="Insights generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/forecast", response_model=AnalyticsResponse)
async def forecast_performance(
    request: ForecastRequest,
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Forecast future performance
    
    - **historical_data**: Historical performance data
    - **days_ahead**: Number of days to forecast
    
    Returns predicted values and growth rate
    """
    await get_current_user(authorization)  # IDOR fix · auth requerida (anti-abuso de cómputo)
    try:
        result = await analytics_agent.execute({
            "type": "forecast",
            "historical_data": request.historical_data,
            "days_ahead": request.days_ahead
        })
        
        return AnalyticsResponse(
            success=True,
            data=result,
            message="Forecast generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dashboard-data", response_model=AnalyticsResponse)
async def get_dashboard_data(
    request: DashboardRequest,
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Get comprehensive dashboard data
    
    - **filters**: Optional filters for data
    
    Returns overview, recent performance, and top posts
    """
    await get_current_user(authorization)  # IDOR fix · auth requerida (anti-abuso de cómputo)
    try:
        result = await analytics_agent.execute({
            "type": "dashboard",
            "filters": request.filters or {}
        })
        
        return AnalyticsResponse(
            success=True,
            data=result,
            message="Dashboard data retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Get Analytics Agent status"""
    await get_current_user(authorization)  # IDOR fix · auth requerida
    return analytics_agent.get_status()


@router.get("/dashboard/", response_model=AnalyticsResponse)
async def get_dashboard(
    client_id: Optional[str] = Query(None, description="Client UUID · None = aggregate-all (solo owner)"),
    date_range: str = Query(default="7d", description="Time range: 7d, 30d, 90d"),
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Get analytics dashboard with real Supabase data

    - **client_id**: Optional client UUID (if None, aggregate all clients)
    - **date_range**: Time range (7d, 30d, 90d)

    Returns content_generated, scheduled_posts, client_context stats
    """
    # IDOR fix: None → aggregate-all gated a owner (require_superadmin) · con client_id → ownership
    # vía resolve_client_or_403 (variante A · calendar_v3._access · sin fallback · molde 5727dda).
    if client_id is None:
        await require_superadmin(authorization)
        validated_client_id: Optional[str] = None
    else:
        user = await get_current_user(authorization)
        client = resolve_client_or_403(user["id"], client_id)
        validated_client_id = str(client["id"])
    result = await handle_get_dashboard(client_id=validated_client_id, date_range=date_range)
    return AnalyticsResponse(
        success=True,
        data=result,
        message="Dashboard data retrieved successfully"
    )
