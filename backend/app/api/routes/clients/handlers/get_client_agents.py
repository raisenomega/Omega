"""
Handler: Client Agents
GET /clients/{client_id}/agents/ - List agents assigned to client
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_client_agents(client_id: str) -> Dict[str, Any]:
    """
    Get agents assigned to this client

    Args:
        client_id: Client UUID

    Returns:
        Dict with agents array and total count

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Check if client exists
        client_resp = supabase.client.table("clients")\
            .select("id")\
            .eq("id", client_id)\
            .single()\
            .execute()

        if not client_resp.data:
            raise HTTPException(status_code=404, detail="Client not found")

        # Get agents from client_context
        agents_resp = supabase.client.table("client_context")\
            .select("*")\
            .eq("client_id", client_id)\
            .execute()

        agents_data = agents_resp.data or []
        agents = [
            {
                "agent_code": agent.get("agent_code"),
                "name": f"{agent.get('agent_code')} — {agent.get('name', 'Agent')}",
                "type": "technical",
                "status": agent.get("status", "active"),
                "last_used": agent.get("last_used"),
                "executions_total": agent.get("executions_total", 0)
            }
            for agent in agents_data
        ]

        return {"agents": agents, "total": len(agents)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting client agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get client agents: {str(e)}")
