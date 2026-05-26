"""
Client Home Dashboard Handler
GET /clients/{client_id}/home
Returns complete dashboard data: profile, social accounts, upcoming posts, stats
Pattern follows: calendar/handlers/list_posts.py (direct Supabase queries)
"""
from fastapi import HTTPException, Header
from typing import Optional
from datetime import datetime, timezone, timedelta
import logging
import calendar

from app.api.routes.clients.models import (
    ClientHomeResponse,
    ClientHomeData,
    ClientHomeStats,
    ClientProfile
)
from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.repositories.client_repository import client_repository
from app.infrastructure.repositories.social_account_repository import social_account_repository
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def get_client_home(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> ClientHomeResponse:
    """
    Get complete client home dashboard.
    Includes: profile, social accounts, upcoming posts (7 days), stats.

    Args:
        client_id: Client UUID
        authorization: Bearer token

    Returns:
        ClientHomeResponse with complete dashboard data

    Raises:
        403: If user lacks permission to access this client
        404: If client not found
    """
    try:
        # 1. Get authenticated user with role
        user = await get_current_user(authorization)
        role = user["role"]
        authenticated_id = user["id"]

        # 2. Verify client exists
        client_data = await client_repository.get_client(client_id)
        if not client_data:
            raise HTTPException(status_code=404, detail="Client not found")

        # 3. Role-based access control (same as social_accounts/list.py)
        if role == "reseller" and client_data.get("reseller_id") != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Resellers can only access their own clients"
            )
        elif role == "client" and client_id != authenticated_id:
            raise HTTPException(
                status_code=403,
                detail="Clients can only access their own data"
            )
        # owner → full access (no check needed)

        # 4. Get social accounts
        social_accounts_data = await social_account_repository.list_accounts(
            client_id=client_id,
            platform=None  # all platforms
        )

        # 5. Get upcoming posts (next 7 days) - direct Supabase query like list_posts.py
        supabase = get_supabase_service()
        today = datetime.now(timezone.utc).date()
        seven_days_ahead = today + timedelta(days=7)

        upcoming_response = supabase.client.table("scheduled_posts")\
            .select("*")\
            .eq("client_id", client_id)\
            .gte("scheduled_for", today.isoformat())\
            .lte("scheduled_for", seven_days_ahead.isoformat())\
            .order("scheduled_for", desc=False)\
            .execute()

        upcoming_posts_data = upcoming_response.data if upcoming_response.data else []

        # 6. Calculate stats
        # Get current month's first and last day
        now = datetime.now(timezone.utc)
        first_day = datetime(now.year, now.month, 1, tzinfo=timezone.utc).date()
        last_day_num = calendar.monthrange(now.year, now.month)[1]
        last_day = datetime(now.year, now.month, last_day_num, 23, 59, 59, tzinfo=timezone.utc).date()

        # Count posts this month
        month_response = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("client_id", client_id)\
            .gte("scheduled_for", first_day.isoformat())\
            .lte("scheduled_for", last_day.isoformat())\
            .execute()

        month_count = month_response.count if hasattr(month_response, 'count') else 0

        # Count all posts
        all_response = supabase.client.table("scheduled_posts")\
            .select("id", count="exact")\
            .eq("client_id", client_id)\
            .execute()

        all_count = all_response.count if hasattr(all_response, 'count') else 0

        # Count connected accounts
        connected_accounts = len([acc for acc in social_accounts_data if acc.get("status") == "active"])

        stats = ClientHomeStats(
            total_posts=all_count,
            connected_accounts=connected_accounts,
            this_month_posts=month_count
        )

        # 7. Build response
        profile = ClientProfile(**client_data)

        home_data = ClientHomeData(
            profile=profile,
            social_accounts=social_accounts_data,
            upcoming_posts=upcoming_posts_data,
            stats=stats
        )

        return ClientHomeResponse(
            success=True,
            data=home_data,
            message="Client home dashboard loaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading client home dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while loading dashboard"
        )
