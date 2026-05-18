"""
Reseller Dashboard Routes
Dashboard data aggregation for reseller UI
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{reseller_id}/dashboard", response_model=APIResponse)
async def get_reseller_dashboard(reseller_id: str) -> APIResponse:
    """
    Get complete reseller dashboard data

    Args:
        reseller_id: Reseller UUID

    Returns:
        APIResponse with comprehensive dashboard data

    Raises:
        HTTPException 404: Reseller not found
        HTTPException 500: Server error

    Response includes:
        - reseller: Full reseller object
        - clients: List of all clients with metrics
        - agents: List of human agents
        - total_revenue: Monthly revenue reported
        - omega_commission: Commission owed to OMEGA
        - active_clients_count: Count of active clients
        - suspended_clients_count: Count of suspended clients
    """
    try:
        service = get_supabase_service()

        # Get reseller
        reseller = await service.get_reseller(reseller_id)
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller not found")

        # Get clients
        clients = await service.get_reseller_clients(reseller_id)

        # Get agents
        agents = await service.get_reseller_agents(reseller_id)

        # Calculate metrics
        total_revenue = reseller.get("monthly_revenue_reported", 0)
        omega_commission_rate = reseller.get("omega_commission_rate", 0.30)
        omega_commission = total_revenue * omega_commission_rate

        active_clients_count = len(
            [c for c in clients if c.get("status") == "active"]
        )
        suspended_clients_count = len(
            [c for c in clients if c.get("status") == "suspended"]
        )

        dashboard_data: Dict[str, Any] = {
            "reseller": reseller,
            "clients": clients,
            "agents": agents,
            "total_revenue": total_revenue,
            "omega_commission": omega_commission,
            "active_clients_count": active_clients_count,
            "suspended_clients_count": suspended_clients_count
        }

        return APIResponse(
            success=True,
            data=dashboard_data,
            message="Dashboard loaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
