"""
OMEGA Company Router - Super Admin Dashboard
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query, Header
from typing import Optional
from pydantic import BaseModel, Field

from .handlers import (
    handle_get_omega_dashboard,
    handle_get_resellers,
    handle_get_clients,
    handle_get_revenue,
    handle_get_activity,
    handle_get_agents,
    handle_get_org_chart,
    handle_generate_dept_report,
    handle_trigger_worker
)

router = APIRouter(prefix="/omega", tags=["omega"])


# Request Models
class DepartmentReportRequest(BaseModel):
    """Request for department performance report"""
    department: str = Field(..., description="Department name (e.g., 'security', 'content', 'analytics')")
    requested_by: str = Field(..., description="User requesting the report")


@router.get("/dashboard/")
async def get_omega_dashboard():
    """Get OMEGA Company executive dashboard with Stripe + Supabase data"""
    return await handle_get_omega_dashboard()


@router.get("/resellers/")
async def get_resellers(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, description="Results per page"),
    offset: int = Query(default=0, description="Pagination offset")
):
    """Get resellers list with metrics"""
    return await handle_get_resellers(status, limit, offset)


@router.get("/clients/")
async def get_clients(
    reseller_id: Optional[str] = Query(None, description="Filter by reseller UUID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, description="Results per page"),
    offset: int = Query(default=0, description="Pagination offset")
):
    """Get all clients with pagination"""
    return await handle_get_clients(reseller_id, status, limit, offset)


@router.get("/revenue/")
async def get_revenue():
    """Get revenue breakdown from Stripe"""
    return await handle_get_revenue()


@router.get("/activity/")
async def get_activity(
    limit: int = Query(default=50, description="Number of activity items")
):
    """Get recent activity feed"""
    return await handle_get_activity(limit)


@router.get("/agents/")
async def get_agents():
    """Get all agents organized by department with stats"""
    return await handle_get_agents()


@router.get("/org-chart/")
async def get_org_chart():
    """Get OMEGA Company organizational chart with 45 agents"""
    return await handle_get_org_chart()


@router.post("/department-report/")
async def generate_department_report(
    request: DepartmentReportRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate department performance report (owner only)

    For security department: crosses omega_agents with sentinel_scans
    For other departments: uses omega_agents + Claude analysis
    """
    return await handle_generate_dept_report(
        department=request.department,
        requested_by=request.requested_by,
        authorization=authorization
    )


@router.post("/workers/{worker_name}/trigger/")
async def trigger_worker(worker_name: str, client_id: Optional[str] = None):
    """
    Dispara un worker manualmente — solo owner

    Si client_id se provee → ejecuta para ese cliente específico
    Si no → ejecuta para todos los clientes activos

    Workers disponibles: news_monitor
    """
    return await handle_trigger_worker(worker_name, client_id)
