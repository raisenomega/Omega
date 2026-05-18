"""
OMEGA · GET /api/v1/reseller/{reseller_id}/clients/
Handler para listar todos los clientes de un reseller
R-LINES-001: < 200L · R-DDD-001: Router → Handler → Supabase
"""
from datetime import datetime, timezone
from fastapi import HTTPException, status, Header
from typing import Optional

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

from .reseller_clients_models import (
    ResellerClientListResponse,
    ResellerClientListData,
    ResellerClientItem,
)
from .reseller_home_helpers import (
    compute_client_health,
    build_client_alerts,
    get_client_revenue,
    RESELLER_PLAN_CAPACITY,
)

TODAY = datetime.now(timezone.utc).date().isoformat()


async def get_reseller_clients(
    reseller_id: str,
    authorization: Optional[str] = Header(None),
) -> ResellerClientListResponse:
    """
    Lista todos los clientes asignados a un reseller.
    Acceso: role=reseller (propio ID) o role=owner (cualquier ID).
    """
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    # ── AUTH CHECK ────────────────────────────────────────────────────────────
    if user.get("role") not in ("reseller", "owner"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado - requiere role reseller u owner"
        )

    # ── FETCH RESELLER ────────────────────────────────────────────────────────
    reseller_row = (
        supabase.client.table("resellers")
        .select("*")
        .eq("id", reseller_id)
        .single()
        .execute()
    )
    if not reseller_row.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reseller no encontrado"
        )

    r = reseller_row.data
    # TODO: Add plan column to resellers table or determine dynamically
    reseller_plan = "agency_starter"  # Default for now
    max_clients = RESELLER_PLAN_CAPACITY.get(reseller_plan, 5)

    # ── FETCH CLIENTS ─────────────────────────────────────────────────────────
    clients_rows = (
        supabase.client.table("clients")
        .select("*")
        .eq("reseller_id", reseller_id)
        .execute()
    )
    raw_clients = clients_rows.data or []

    clients_list: list[ResellerClientItem] = []

    for c in raw_clients:
        cid = c["id"]
        plan = c.get("plan", "basic")

        # ── FETCH SOCIAL ACCOUNTS ─────────────────────────────────────────────
        accounts_rows = (
            supabase.client.table("social_accounts")
            .select("*")
            .eq("client_id", cid)
            .execute()
        )
        accounts = accounts_rows.data or []

        # ── FETCH POSTS THIS MONTH ────────────────────────────────────────────
        posts_rows = (
            supabase.client.table("scheduled_posts")
            .select("*")
            .eq("client_id", cid)
            .gte("scheduled_date", datetime.now(timezone.utc).replace(day=1).date().isoformat())
            .execute()
        )
        posts = posts_rows.data or []
        posts_month = len(posts)

        # ── COMPUTE HEALTH & ALERTS ───────────────────────────────────────────
        last_post = max((p.get("scheduled_date", "") for p in posts), default=None)
        alerts = build_client_alerts(c, accounts, posts_month, plan, last_post)
        health = compute_client_health(accounts, posts_month, plan, last_post)

        clients_list.append(
            ResellerClientItem(
                id=cid,
                name=c.get("name", ""),
                email=c.get("email", ""),
                plan=plan,
                status=c.get("status", "active"),
                health=health,
                posts_this_month=posts_month,
                connected_accounts=len([a for a in accounts if a.get("connected")]),
                total_accounts=len(accounts),
                alerts_count=len(alerts),
                last_post_date=last_post,
                revenue_monthly=get_client_revenue(plan),
            )
        )

    return ResellerClientListResponse(
        success=True,
        data=ResellerClientListData(
            clients=clients_list,
            total_clients=len(raw_clients),
            reseller_id=reseller_id,
            reseller_name=r.get("owner_name", ""),
            reseller_plan=reseller_plan,
            max_clients=max_clients,
        ),
    )
