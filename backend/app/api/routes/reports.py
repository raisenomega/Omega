"""
Reports API Routes
Endpoints for report generation and formatting
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.agents.report_generator_agent import report_generator_agent
from app.services.report_builder import report_builder, ReportMetric

router = APIRouter(prefix="/reports", tags=["reports"])


# Request Models
class MonthlyReportRequest(BaseModel):
    """Request for monthly report"""
    client_name: str = Field(..., description="Client name")
    metrics_data: Dict[str, float] = Field(..., description="Current period metrics")
    previous_period_data: Dict[str, float] = Field(..., description="Previous period metrics")
    agency_notes: str = Field(default="", description="Agency notes")


class CampaignReportRequest(BaseModel):
    """Request for campaign report"""
    client_name: str = Field(..., description="Client name")
    campaign_name: str = Field(..., description="Campaign name")
    campaign_data: Dict[str, float] = Field(..., description="Campaign metrics")
    goals: Dict[str, float] = Field(..., description="Campaign goals")


class ExecutiveSummaryRequest(BaseModel):
    """Request for executive summary"""
    metrics: List[Dict[str, Any]] = Field(..., description="Metrics list")
    client_name: str = Field(..., description="Client name")
    period: str = Field(..., description="Report period")


class FormatMarkdownRequest(BaseModel):
    """Request for markdown formatting"""
    report: Dict[str, Any] = Field(..., description="Report data")


# Response Model
class ReportsAPIResponse(BaseModel):
    """Generic reports response"""
    success: bool
    data: dict
    message: str | None = None


@router.post("/generate-monthly", response_model=ReportsAPIResponse)
async def generate_monthly_report(
    request: MonthlyReportRequest
) -> ReportsAPIResponse:
    """
    Generate comprehensive monthly report

    - **client_name**: Client name
    - **metrics_data**: Current period metrics
    - **previous_period_data**: Previous period metrics for comparison
    - **agency_notes**: Optional notes from agency team

    Returns complete executive report with insights and recommendations
    """
    try:
        result = await report_generator_agent.execute({
            "type": "generate_monthly",
            "client_name": request.client_name,
            "metrics_data": request.metrics_data,
            "previous_period_data": request.previous_period_data,
            "agency_notes": request.agency_notes
        })

        return ReportsAPIResponse(
            success=True,
            data=result,
            message="Monthly report generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-campaign", response_model=ReportsAPIResponse)
async def generate_campaign_report(
    request: CampaignReportRequest
) -> ReportsAPIResponse:
    """
    Generate campaign performance report

    - **client_name**: Client name
    - **campaign_name**: Campaign name
    - **campaign_data**: Campaign metrics
    - **goals**: Campaign goals for comparison

    Returns campaign report with goal vs actual analysis
    """
    try:
        result = await report_generator_agent.execute({
            "type": "generate_campaign",
            "client_name": request.client_name,
            "campaign_name": request.campaign_name,
            "campaign_data": request.campaign_data,
            "goals": request.goals
        })

        return ReportsAPIResponse(
            success=True,
            data=result,
            message="Campaign report generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/executive-summary", response_model=ReportsAPIResponse)
async def write_executive_summary(
    request: ExecutiveSummaryRequest
) -> ReportsAPIResponse:
    """
    Generate executive summary from metrics

    - **metrics**: List of metrics data
    - **client_name**: Client name
    - **period**: Report period

    Returns professionally written executive summary
    """
    try:
        # Convert dict metrics to ReportMetric objects
        metrics = [ReportMetric(**m) for m in request.metrics]

        result = await report_generator_agent.execute({
            "type": "executive_summary",
            "metrics": metrics,
            "client_name": request.client_name,
            "period": request.period
        })

        return ReportsAPIResponse(
            success=True,
            data={"summary": result},
            message="Executive summary generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/format-markdown", response_model=ReportsAPIResponse)
async def format_report_markdown(
    request: FormatMarkdownRequest
) -> ReportsAPIResponse:
    """
    Format report as markdown

    - **report**: Report data to format

    Returns markdown-formatted report
    """
    try:
        result = await report_generator_agent.execute({
            "type": "format_markdown",
            "report": request.report
        })

        return ReportsAPIResponse(
            success=True,
            data={"markdown": result},
            message="Report formatted as markdown"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_report_templates() -> dict:
    """Get available report templates"""
    templates = [
        {
            "id": "monthly",
            "name": "Monthly Performance Report",
            "description": "Comprehensive monthly analysis"
        },
        {
            "id": "campaign",
            "name": "Campaign Results Report",
            "description": "Campaign performance vs goals"
        }
    ]

    return {"templates": templates}


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Report Generator Agent status"""
    return report_generator_agent.get_status()
