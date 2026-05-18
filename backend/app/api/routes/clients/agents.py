"""
Client Agents Endpoint
GET /clients/{client_id}/agents/ - List agents assigned to client
POST /clients/{client_id}/agents/assign/ - Assign agents to client
"""
from fastapi import APIRouter, Header
from typing import Optional, List
from pydantic import BaseModel
from app.api.routes.clients.handlers import handle_get_client_agents, handle_assign_client_agents
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter()


class AssignAgentsRequest(BaseModel):
    agent_codes: List[str]


@router.get("/{client_id}/agents/")
async def get_client_agents(
    client_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get agents assigned to this client"""
    await get_current_user(authorization)  # Auth check
    return await handle_get_client_agents(client_id)


@router.post("/{client_id}/agents/assign/")
async def assign_client_agents(
    client_id: str,
    request: AssignAgentsRequest,
    authorization: Optional[str] = Header(None)
):
    """Assign agents to this client"""
    await get_current_user(authorization)  # Auth check
    return await handle_assign_client_agents(client_id, request.agent_codes)
