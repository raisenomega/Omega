"""
Client List Endpoint
GET /clients/ with role-based filtering
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
import logging

from app.api.routes.clients.models import ClientListResponse, ClientProfile
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=ClientListResponse)
async def list_clients(
    authorization: Optional[str] = Header(None),
    status: Optional[str] = Query(None, description="Filter by status"),
    plan: Optional[str] = Query(None, description="Filter by plan"),
    search: Optional[str] = Query(None, description="Search in name or email")
) -> ClientListResponse:
    """
    List clients with role-based access control.
    owner: all clients, reseller: their clients, client: forbidden.
    """
    try:
        # 1. Get authenticated user with role
        user = await get_current_user(authorization)
        user_id = user["id"]
        role = user["role"]
        reseller_id = user.get("reseller_id")

        # 2. Role-based access control
        if role == "client":
            raise HTTPException(
                status_code=403,
                detail="Clients cannot list other clients. Use GET /auth/me for your profile."
            )

        # 3. List clients based on role
        clients_data = await client_repository.list_clients(
            role=role,
            authenticated_id=user_id,
            reseller_id=reseller_id,
            status=status,
            plan=plan,
            search=search
        )

        # 4. Convert to ClientProfile models
        clients = [ClientProfile(**client) for client in clients_data]

        logger.info(f"Listed {len(clients)} clients for role={role}, user={user_id}")

        return ClientListResponse(
            success=True,
            data=clients,
            total=len(clients),
            message=f"Found {len(clients)} client(s)"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing clients: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while listing clients"
        )
