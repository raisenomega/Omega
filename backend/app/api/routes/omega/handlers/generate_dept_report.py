"""
Handler: Generate Department Report
Cruza omega_agents con sentinel_scans para reportes reales
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, Header
from datetime import datetime
import logging

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service
from ._dept_report_security import _generate_security_report
from ._dept_report_standard import _generate_standard_report

logger = logging.getLogger(__name__)


async def handle_generate_dept_report(
    department: str,
    requested_by: str,
    authorization: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Generate department performance report.
    Security: crosses omega_agents + sentinel_scans.
    Other departments: omega_agents + Claude analysis.
    Owner-only endpoint.
    """
    try:
        user = await get_current_user(authorization)
        if user.get("role") != "owner":
            raise HTTPException(status_code=403, detail="Solo superadmin puede generar reportes")

        supabase = get_supabase_service()

        agents_resp = supabase.client.table("omega_agents")\
            .select("*")\
            .eq("department", department)\
            .order("role", desc=True).order("agent_code")\
            .execute()

        agents = agents_resp.data or []

        if not agents:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron agentes para el departamento: {department}",
            )

        director = None
        sub_agents = []
        for agent in agents:
            if agent.get("role") == "director":
                director = agent
            else:
                sub_agents.append(agent)

        if department.lower() == "security":
            report_data = await _generate_security_report(supabase, director, sub_agents, requested_by)
        else:
            report_data = await _generate_standard_report(
                supabase, department, director, sub_agents, requested_by
            )

        logger.info(f"Department report generated: {department} by {requested_by}")
        return report_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating department report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
