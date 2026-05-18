"""
Analytics API Routes
Endpoints for data analysis and insights
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.agents.analytics_agent import analytics_agent
from app.api.routes.analytics.handlers.get_dashboard import handle_get_dashboard

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
async def analyze_metrics(request: AnalyzeMetricsRequest) -> AnalyticsResponse:
    """
    Analyze social media metrics
    
    - **data**: Metrics including likes, comments, shares, followers, impressions
    
    Returns engagement rate, reach percentage, and AI-generated insights
    """
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
async def detect_patterns(request: DetectPatternsRequest) -> AnalyticsResponse:
    """
    Detect patterns in historical data
    
    - **historical_data**: List of data points with timestamps and values
    
    Returns moving averages, anomalies, growth trends, and AI analysis
    """
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
async def generate_insights(request: GenerateInsightsRequest) -> AnalyticsResponse:
    """
    Generate actionable insights from metrics
    
    - **metrics**: Dictionary of metrics to analyze
    
    Returns AI-generated insights with observations and action items
    """
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
async def forecast_performance(request: ForecastRequest) -> AnalyticsResponse:
    """
    Forecast future performance
    
    - **historical_data**: Historical performance data
    - **days_ahead**: Number of days to forecast
    
    Returns predicted values and growth rate
    """
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
async def get_dashboard_data(request: DashboardRequest) -> AnalyticsResponse:
    """
    Get comprehensive dashboard data
    
    - **filters**: Optional filters for data
    
    Returns overview, recent performance, and top posts
    """
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
async def get_agent_status() -> dict:
    """Get Analytics Agent status"""
    return analytics_agent.get_status()


@router.get("/dashboard/", response_model=AnalyticsResponse)
async def get_dashboard(
    client_id: Optional[str] = Query(None, description="Optional client UUID (aggregate all if None)"),
    date_range: str = Query(default="7d", description="Time range: 7d, 30d, 90d")
) -> AnalyticsResponse:
    """
    Get analytics dashboard with real Supabase data

    - **client_id**: Optional client UUID (if None, aggregate all clients)
    - **date_range**: Time range (7d, 30d, 90d)

    Returns content_generated, scheduled_posts, agent_executions, client_context stats
    """
    result = await handle_get_dashboard(client_id, date_range)
    return AnalyticsResponse(
        success=True,
        data=result,
        message="Dashboard data retrieved successfully"
    )
