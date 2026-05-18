"""
Client Create Endpoint
POST /clients/ - Create new client account
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging
from datetime import datetime, timezone

from app.api.routes.clients.models import ClientCreate, ClientResponse, ClientProfile
from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.auth.jwt_utils import hash_password
from app.infrastructure.repositories.client_repository import client_repository

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ClientResponse)
async def create_client(
    request: ClientCreate,
    authorization: Optional[str] = Header(None)
) -> ClientResponse:
    """
    Create new client account.
    Only owner and reseller can create. Resellers auto-assign their ID.
    """
    try:
        # 1. Get authenticated user with role
        user = await get_current_user(authorization)
        user_role = user["role"]
        user_id = user["id"]

        # 2. Role-based access control
        if user_role == "client":
            raise HTTPException(
                status_code=403,
                detail="Clients cannot create other clients. Contact your reseller."
            )

        # 3. Check email uniqueness
        existing_client = await client_repository.get_client_by_email(request.email)
        if existing_client:
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

        # 4. Hash password with bcrypt (12 rounds via jwt_utils)
        password_hash = hash_password(request.password)

        # 5. Determine reseller_id based on creator role
        reseller_id = None
        if user_role == "reseller":
            reseller_id = user_id
        elif user_role == "owner" and request.reseller_id:
            reseller_id = request.reseller_id

        # 6. Build client data with defaults
        client_data = {
            "email": request.email,
            "name": request.name,
            "password_hash": password_hash,
            "phone": request.phone,
            "company": request.company,
            "plan": request.plan,
            "notes": request.notes,
            "role": "client",
            "status": "active",
            "subscription_status": "trial",
            "trial_active": True,
            "reseller_id": reseller_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 7. Create client in database
        created_client = await client_repository.create_client(client_data)

        logger.info(
            f"Client created by {user_role} {user_id}: "
            f"{created_client['email']} (reseller_id={reseller_id})"
        )

        return ClientResponse(
            success=True,
            data=ClientProfile(**created_client),
            message="Client created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while creating client"
        )
