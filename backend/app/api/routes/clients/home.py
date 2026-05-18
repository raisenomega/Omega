"""
Client Home Endpoint
GET /clients/{client_id}/home
"""
from fastapi import APIRouter, Header
from typing import Optional

from app.api.routes.clients.models import ClientHomeResponse
from app.api.routes.clients.handlers.get_client_home import get_client_home

router = APIRouter()


@router.get("/{client_id}/home/", response_model=ClientHomeResponse)
async def client_home(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> ClientHomeResponse:
    """
    Get complete client home dashboard.

    Returns:
        - Client profile
        - Social accounts list
        - Upcoming posts (next 7 days)
        - Stats: total posts, connected accounts, this month posts

    Requires authentication. Role-based access:
    - **owner**: Access to all clients
    - **reseller**: Only their own clients
    - **client**: Only their own data
    """
    return await get_client_home(client_id, authorization)
