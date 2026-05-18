"""Handler: Assign agents to client"""
import logging
from typing import Dict, Any, List
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

async def handle_assign_client_agents(client_id: str, agent_codes: List[str]) -> Dict[str, Any]:
    """Assigns agents to client by UPSERTING client_context records"""
    try:
        supabase = get_supabase_service()
        # Verify client exists
        client_resp = supabase.client.table("clients").select("id").eq("id", client_id).single().execute()
        if not client_resp.data:
            return {"error": "Client not found", "assigned": [], "skipped": agent_codes, "total_assigned": 0}
        assigned = []
        skipped = []
        # Assign each agent
        for agent_code in agent_codes:
            try:
                # Get agent name from omega_agents
                agent_resp = supabase.client.table("omega_agents")\
                    .select("agent_code, name")\
                    .eq("agent_code", agent_code)\
                    .single()\
                    .execute()
                if not agent_resp.data:
                    logger.warning(f"Agent {agent_code} not found")
                    skipped.append(agent_code)
                    continue
                agent_name = agent_resp.data.get("name", agent_code)
                # UPSERT into client_context
                supabase.client.table("client_context").upsert({
                    "client_id": client_id,
                    "agent_code": agent_code,
                    "name": agent_name,
                    "status": "active",
                    "last_used": None,
                    "executions_total": 0
                }, on_conflict="client_id,agent_code").execute()
                assigned.append(agent_code)
                logger.info(f"Assigned {agent_code} to client {client_id}")
            except Exception as e:
                logger.error(f"Error assigning {agent_code}: {e}")
                skipped.append(agent_code)
        return {"assigned": assigned, "skipped": skipped, "total_assigned": len(assigned)}
    except Exception as e:
        logger.error(f"Error in handle_assign_client_agents: {e}")
        return {"error": str(e), "assigned": [], "skipped": agent_codes, "total_assigned": 0}
