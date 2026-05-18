"""
OMEGA · GET /api/v1/reseller/{reseller_id}/home/
Handler principal para el dashboard del reseller
R-LINES-001: < 200L · R-DDD-001: Router → Handler → Supabase
"""
from datetime import datetime, timezone
from fastapi import HTTPException, status, Header
from typing import Optional

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

from .reseller_home_models import (
    ResellerHomeResponse, ResellerHomeData, ResellerProfile,
    ResellerKPIs, ResellerClientData, ResellerClientStats,
    ResellerSocialAccount, ResellerUpcomingPost,
)
from .reseller_home_helpers import (
    compute_client_health, build_client_alerts,
    build_upsell_opportunities, get_client_revenue,
    RESELLER_PLAN_CAPACITY,
)

TODAY = datetime.now(timezone.utc).date().isoformat()


async def get_reseller_home(
    reseller_id: str,
    authorization: Optional[str] = Header(None),
) -> ResellerHomeResponse:
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") not in ("reseller", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    reseller_row = supabase.client.table("resellers").select("*").eq("id", reseller_id).single().execute()
    if not reseller_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reseller no encontrado")

    r = reseller_row.data
    reseller_plan = r.get("plan") or None
    if not reseller_plan:
        client_row = supabase.client.table("clients").select("plan").eq("id", reseller_id).limit(1).execute()
        reseller_plan = (client_row.data[0].get("plan") if client_row.data else None) or "agency_starter"
    max_clients = RESELLER_PLAN_CAPACITY.get(reseller_plan, 5)

    clients_rows = supabase.client.table("clients").select("*").eq("reseller_id", reseller_id).execute()
    raw_clients = clients_rows.data or []

    clients_data: list[ResellerClientData] = []
    total_posts = 0
    total_alerts = 0
    health_counts = {"green": 0, "yellow": 0, "red": 0}
    mrr = 0.0

    upsell_input: list[dict] = []

    for c in raw_clients:
        cid = c["id"]
        plan = c.get("plan", "basic")
        mrr += get_client_revenue(plan)

        accounts_rows = supabase.client.table("social_accounts").select("*").eq("client_id", cid).execute()
        accounts = accounts_rows.data or []

        posts_rows = (
            supabase.client.table("scheduled_posts")
            .select("*")
            .eq("client_id", cid)
            .gte("scheduled_date", datetime.now(timezone.utc).replace(day=1).date().isoformat())
            .execute()
        )
        posts = posts_rows.data or []
        posts_month = len(posts)
        total_posts += posts_month

        upcoming = [p for p in posts if p.get("scheduled_date", "") >= TODAY][:5]
        last_post = max((p.get("scheduled_date", "") for p in posts), default=None)

        social = [
            ResellerSocialAccount(
                id=a["id"], platform=a.get("platform",""),
                username=a.get("username"), connected=a.get("connected", False),
                is_active=a.get("is_active", False),
            ) for a in accounts
        ]

        alerts = build_client_alerts(c, accounts, posts_month, plan, last_post)
        total_alerts += len(alerts)

        health = compute_client_health(accounts, posts_month, plan, last_post)
        health_counts[health] = health_counts.get(health, 0) + 1

        up_posts = [
            ResellerUpcomingPost(
                id=p["id"], scheduled_date=p.get("scheduled_date",""),
                scheduled_time=p.get("scheduled_time"), text_content=p.get("text_content"),
                status=p.get("status","pending"), platform=p.get("platform"),
                has_connected_account=any(
                    a.get("platform") == p.get("platform") and a.get("connected")
                    for a in accounts
                ),
            ) for p in upcoming
        ]

        upsell_input.append({
            "id": cid, "name": c.get("name",""), "plan": plan,
            "posts_month": posts_month, "connected_accounts": len([a for a in accounts if a.get("connected")]),
            "days_since_created": 0,
        })

        clients_data.append(ResellerClientData(
            id=cid, name=c.get("name",""), email=c.get("email",""),
            plan=plan, status=c.get("status","active"), health=health,
            social_accounts=social, upcoming_posts=up_posts,
            stats=ResellerClientStats(
                posts_this_month=posts_month, connected_accounts=len([a for a in accounts if a.get("connected")]),
                total_accounts=len(accounts), revenue_monthly=get_client_revenue(plan), plan=plan,
            ),
            alerts=alerts, last_activity_days=0,
        ))

    profile = ResellerProfile(
        id=r["id"], email=r.get("owner_email",""), name=r.get("owner_name",""),
        company=r.get("agency_name"), plan=reseller_plan, reseller_plan=reseller_plan,
        max_clients=max_clients, active_clients=len(raw_clients),
        payment_status=r.get("status","active") or "active",
    )

    kpis = ResellerKPIs(
        mrr_generated=mrr, mrr_prev_month=mrr, mrr_delta=0.0,
        total_posts_month=total_posts, active_alerts=total_alerts,
        healthy_clients=health_counts["green"],
        warning_clients=health_counts["yellow"],
        critical_clients=health_counts["red"],
    )

    return ResellerHomeResponse(
        success=True,
        data=ResellerHomeData(
            profile=profile, kpis=kpis, clients=clients_data,
            agent_reports=[], upsell_opportunities=build_upsell_opportunities(upsell_input),
        ),
    )
