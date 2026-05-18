"""
Auth Registration Routes
Endpoint for client registration with JWT token generation
"""
from fastapi import APIRouter, HTTPException
from app.models.shared_models import APIResponse
from app.api.routes.auth.models import RegisterRequest
from app.api.routes.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    hash_password,
)
from app.infrastructure.supabase_service import get_supabase_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=APIResponse)
async def register(request: RegisterRequest) -> APIResponse:
    """
    Register new client account

    Args:
        request: RegisterRequest with name, email, password, plan, reseller_id

    Returns:
        APIResponse with:
            - success: True
            - data: Client object (id, name, email, plan, role, reseller_id)
            - token: JWT access token (7-day expiration)
            - refresh_token: JWT refresh token (30-day expiration)
            - message: Success message

    Raises:
        HTTPException 400: Email already exists
        HTTPException 404: Invalid reseller_id
        HTTPException 500: Server error

    Flow:
        1. Validate email uniqueness
        2. Validate reseller_id if provided
        3. Hash password with bcrypt (via hash_password())
        4. Insert into clients table with trial defaults
        5. Generate JWT tokens with full client data
        6. Return client data + tokens
    """
    try:
        service = get_supabase_service()

        # Check if email already exists
        existing_client = service.client.table("clients")\
            .select("id, email")\
            .eq("email", request.email)\
            .execute()

        if existing_client.data and len(existing_client.data) > 0:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # If reseller_id provided, verify it exists
        if request.reseller_id:
            reseller = service.client.table("resellers")\
                .select("id")\
                .eq("id", request.reseller_id)\
                .execute()

            if not reseller.data or len(reseller.data) == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Invalid reseller_id"
                )

        # Hash password using bcrypt (12 rounds)
        password_hash = hash_password(request.password)

        # Create client data with trial defaults
        client_data = {
            "name": request.name,
            "email": request.email,
            "password_hash": password_hash,
            "plan": request.plan,
            "role": "client",
            "status": "active",
            "subscription_status": "trial",
            "trial_active": True,
        }

        # Add reseller_id if provided
        if request.reseller_id:
            client_data["reseller_id"] = request.reseller_id

        # Insert into clients table
        insert_response = service.client.table("clients")\
            .insert(client_data)\
            .execute()

        if not insert_response.data or len(insert_response.data) == 0:
            raise HTTPException(
                status_code=500,
                detail="Failed to create client account"
            )

        client = insert_response.data[0]

        # Generate JWT tokens with full client data
        access_token = create_access_token({
            "id": client["id"],
            "email": client["email"],
            "role": client.get("role", "client"),
            "reseller_id": client.get("reseller_id"),
        })
        refresh_token = create_refresh_token(client["id"])

        # Remove password_hash from response
        client.pop("password_hash", None)

        logger.info(f"Client registered successfully: {client['email']}")

        return APIResponse(
            success=True,
            data=client,
            token=access_token,
            refresh_token=refresh_token,
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering client: {e}")
        raise HTTPException(status_code=500, detail=str(e))
