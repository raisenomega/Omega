"""
Monitor API Routes
Endpoints for system monitoring and health checks
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.monitor_agent import monitor_agent
from app.services.health_checker import SystemAnomaly

router = APIRouter(prefix="/monitor", tags=["monitor"])


# Request Models
class CheckAgentRequest(BaseModel):
    """Request for agent health check"""
    agent_id: str = Field(..., description="Agent identifier")
    metrics: Dict[str, Any] = Field(default={}, description="Performance metrics")


class DetectAnomaliesRequest(BaseModel):
    """Request for anomaly detection"""
    metrics_history: List[Dict[str, Any]] = Field(
        ...,
        description="Historical metrics data"
    )


# Response Model
class MonitorAPIResponse(BaseModel):
    """Generic monitor response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.get("/system-health", response_model=MonitorAPIResponse)
async def get_system_health() -> MonitorAPIResponse:
    """
    Get overall system health status
    
    Returns health status of all agents and services
    """
    try:
        result = await monitor_agent.execute({
            "type": "system_health"
        })
        
        return MonitorAPIResponse(
            success=True,
            data=result.model_dump(),
            message="System health checked successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents-status", response_model=MonitorAPIResponse)
async def get_agents_status() -> MonitorAPIResponse:
    """
    Get status of all agents
    
    Returns current status of each agent in the system
    """
    try:
        health_report = await monitor_agent.execute({
            "type": "system_health"
        })
        
        return MonitorAPIResponse(
            success=True,
            data={
                "agents": health_report.agents_status,
                "timestamp": health_report.timestamp
            },
            message="Agents status retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-agent", response_model=MonitorAPIResponse)
async def check_agent(request: CheckAgentRequest) -> MonitorAPIResponse:
    """
    Check individual agent performance
    
    - **agent_id**: Agent identifier
    - **metrics**: Performance metrics to analyze
    
    Returns detailed performance report for the agent
    """
    try:
        result = await monitor_agent.execute({
            "type": "agent_performance",
            "agent_id": request.agent_id,
            "metrics": request.metrics
        })
        
        return MonitorAPIResponse(
            success=True,
            data=result.model_dump(),
            message=f"Agent {request.agent_id} checked successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-anomalies", response_model=MonitorAPIResponse)
async def detect_anomalies(
    request: DetectAnomaliesRequest
) -> MonitorAPIResponse:
    """
    Detect system anomalies
    
    - **metrics_history**: Historical metrics data
    
    Returns list of detected anomalies with severity levels
    """
    try:
        result = await monitor_agent.execute({
            "type": "detect_anomalies",
            "metrics_history": request.metrics_history
        })
        
        return MonitorAPIResponse(
            success=True,
            data={
                "anomalies": [a.model_dump() for a in result],
                "count": len(result)
            },
            message=f"Detected {len(result)} anomalies"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts", response_model=MonitorAPIResponse)
async def get_alerts() -> MonitorAPIResponse:
    """
    Get active alerts
    
    Returns list of active system alerts
    """
    try:
        # In production, this would query a database of alerts
        # For now, return empty list
        return MonitorAPIResponse(
            success=True,
            data={
                "alerts": [],
                "active_count": 0
            },
            message="No active alerts"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-status")
async def get_agent_status() -> dict:
    """Get Monitor Agent status"""
    return monitor_agent.get_status()
