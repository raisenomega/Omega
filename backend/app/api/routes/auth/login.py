"""
Auth Login Routes
Endpoint for client login with JWT token generation
"""
from fastapi import APIRouter, HTTPException, Request
from app.models.shared_models import APIResponse
from app.api.routes.auth.models import LoginRequest
from app.api.routes.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_redirect_by_role,
)
from app.infrastructure.supabase_service import get_supabase_service
from app.bc_cognition.application.guardian_session_analyzer import analyze_login
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def _guardian_ip(req: Request) -> str:
    fwd = req.headers.get("x-forwarded-for", "")
    return fwd.split(",")[0].strip() if fwd else (req.client.host if req.client else "")


@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest, http_request: Request) -> APIResponse:
    """
    Login with email and password

    Args:
        request: LoginRequest with email and password

    Returns:
        APIResponse with:
            - success: True
            - data: Client object with redirect_to field
            - token: JWT access token (7-day expiration)
            - refresh_token: JWT refresh token (30-day expiration)
            - message: Success message

    Raises:
        HTTPException 401: Invalid credentials (email not found or password incorrect)
        HTTPException 403: Account inactive
        HTTPException 500: Server error

    Flow:
        1. Query clients table by email
        2. Verify password hash with bcrypt (via verify_password())
        3. Check account status is active
        4. Generate JWT tokens with full client data
        5. Calculate redirect path by role
        6. Return client data + tokens + redirect_to
    """
    try:
        service = get_supabase_service()

        # Query client by email
        client_response = await asyncio.to_thread(
            lambda: service.client.table("clients")
            .select("id, name, email, password_hash, plan, role, reseller_id, status, subscription_status, trial_active")
            .eq("email", request.email)
            .execute()
        )

        if not client_response.data or len(client_response.data) == 0:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        client = client_response.data[0]

        # Verify password using bcrypt
        if not verify_password(request.password, client["password_hash"]):
            await asyncio.to_thread(analyze_login, client["id"], _guardian_ip(http_request),
                                    http_request.headers.get("user-agent", ""), False)  # GUARDIAN 4B-3
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Check if account is active
        if client.get("status") != "active":
            raise HTTPException(
                status_code=403,
                detail="Account is inactive. Contact support."
            )

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

        # For resellers: lookup reseller_id from resellers table
        if client.get("role") == "reseller":
            reseller_response = await asyncio.to_thread(
                lambda: service.client.table("resellers")
                .select("id")
                .eq("owner_email", client["email"])
                .execute()
            )
            if reseller_response.data and len(reseller_response.data) > 0:
                client["reseller_id"] = reseller_response.data[0]["id"]

        # Get redirect path by role
        redirect_to = get_redirect_by_role(client.get("role", "client"))

        logger.info(f"Client logged in successfully: {client['email']}")
        await asyncio.to_thread(analyze_login, client["id"], _guardian_ip(http_request),
                                http_request.headers.get("user-agent", ""), True)  # GUARDIAN 4B-3

        return APIResponse(
            success=True,
            data={
                **client,
                "redirect_to": redirect_to,
            },
            token=access_token,
            refresh_token=refresh_token,
            message="Login successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=str(e))
