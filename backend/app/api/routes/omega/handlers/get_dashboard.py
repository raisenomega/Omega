"""
Handler: OMEGA Company Dashboard - Super Admin Executive View
Real Stripe + Supabase data
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import asyncio
import logging
import os
from datetime import date, timedelta
import stripe

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


async def handle_get_omega_dashboard() -> Dict[str, Any]:
    """
    Get OMEGA Company executive dashboard with real data

    Returns:
        Complete agency metrics: revenue, resellers, clients, content, agents, posts

    Raises:
        HTTPException 500: Database or Stripe error
    """
    try:
        supabase = get_supabase_service()
        today = date.today()
        first_of_month = today.replace(day=1).isoformat()

        # 1. Stripe Revenue Data
        mrr, total_revenue = 0, 0
        try:
            subs = await asyncio.to_thread(stripe.Subscription.list, status='active', limit=100)
            mrr = sum(s.plan.amount / 100 for s in subs.data if s.plan.interval == 'month')
            charges = await asyncio.to_thread(stripe.Charge.list, limit=100)
            total_revenue = sum(c.amount / 100 for c in charges.data if c.paid)
        except Exception as e:
            logger.warning(f"Stripe data unavailable: {e}")
        # 2–8. All Supabase queries in parallel (non-blocking)
        def q_resellers():
            return (supabase.client.table("resellers").select("*").execute()).data or []

        def q_clients():
            return (supabase.client.table("clients").select("id, reseller_id, created_at, status").neq("status", "deleted").execute()).data or []

        def q_content():
            return (supabase.client.table("content_lab_generated").select("id, content_type, created_at").execute()).data or []

        def q_execs():
            return (supabase.client.table("agent_executions").select("id, status, started_at").execute()).data or []

        def q_accounts():
            return (supabase.client.table("social_accounts").select("id, platform, status").eq("status", "active").execute()).data or []

        def q_posts():
            return (supabase.client.table("scheduled_posts").select("id, status, scheduled_for").execute()).data or []

        def q_agents():
            return (supabase.client.table("agents").select("id, code, name, category, model_tier, is_active").eq("is_active", True).order("name").execute()).data or []

        (
            resellers_data, clients_data, content_data,
            exec_data, accounts_data, posts_data, agents_detail_data,
        ) = await asyncio.gather(
            asyncio.to_thread(q_resellers),
            asyncio.to_thread(q_clients),
            asyncio.to_thread(q_content),
            asyncio.to_thread(q_execs),
            asyncio.to_thread(q_accounts),
            asyncio.to_thread(q_posts),
            asyncio.to_thread(q_agents),
        )

        active_resellers = [r for r in resellers_data if r.get("status") == "active"]
        trial_resellers = [r for r in resellers_data if r.get("status") == "trial"]
        new_clients_month = [c for c in clients_data if c.get("created_at", "")[:10] >= first_of_month]
        by_reseller = {}
        for c in clients_data:
            rid = c.get("reseller_id", "direct")
            by_reseller[rid] = by_reseller.get(rid, 0) + 1
        content_month = [c for c in content_data if c.get("created_at", "")[:10] >= first_of_month]
        by_type = {}
        for c in content_data:
            ctype = c.get("content_type", "unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1
        videos_total = by_type.get("video", 0)
        exec_month = [e for e in exec_data if e.get("started_at", "")[:10] >= first_of_month]
        successful = sum(1 for e in exec_data if e.get("status") == "completed")
        success_rate = round((successful / len(exec_data)) * 100, 1) if exec_data else 0
        by_platform = {}
        for acc in accounts_data:
            platform = acc.get("platform", "unknown")
            by_platform[platform] = by_platform.get(platform, 0) + 1
        scheduled = [p for p in posts_data if p.get("status") == "pending"]
        published_month = [p for p in posts_data if p.get("status") in ("published", "published_manual") and p.get("scheduled_for", "")[:10] >= first_of_month]
        next_7days = (today + timedelta(days=7)).isoformat()
        upcoming = [p for p in scheduled if today.isoformat() <= p.get("scheduled_for", "")[:10] <= next_7days]
        by_category = {}
        for agent in agents_detail_data:
            cat = agent.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(agent)
        # `is_active=True` ya filtra el query; todos los devueltos están activos.
        active_agents_count = sum(1 for a in agents_detail_data if a.get("is_active", True))
        logger.info(f"OMEGA Dashboard: {len(resellers_data)} resellers, {len(clients_data)} clients")

        return {
            "agency": {
                "name": "Raisen Agency",
                "plan": "enterprise",
                "mrr": round(mrr, 2),
                "arr": round(mrr * 12, 2),
                "total_revenue": round(total_revenue, 2)
            },
            "resellers": {
                "total": len(resellers_data),
                "active": len(active_resellers),
                "trial": len(trial_resellers),
                "list": resellers_data[:10]
            },
            "clients": {
                "total": len(clients_data),
                "active": len(clients_data),
                "new_this_month": len(new_clients_month),
                "by_reseller": by_reseller
            },
            "content": {
                "generated_total": len(content_data),
                "generated_this_month": len(content_month),
                "by_type": by_type,
                "videos_generated": videos_total
            },
            "agents": {
                "total": len(agents_detail_data),
                "executions_total": len(exec_data),
                "executions_this_month": len(exec_month),
                "success_rate": success_rate
            },
            "agents_detail": {
                "total": len(agents_detail_data),
                "by_category": by_category,
                "active_count": active_agents_count
            },
            "social_accounts": {
                "total": len(accounts_data),
                "by_platform": by_platform
            },
            "scheduled_posts": {
                "total_scheduled": len(scheduled),
                "published_this_month": len(published_month),
                "upcoming_7days": len(upcoming)
            }
        }

    except Exception as e:
        logger.error(f"Error getting OMEGA dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
