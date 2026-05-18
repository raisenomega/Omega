"""
Handler: Analytics Dashboard with real Supabase data
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, Optional
from fastapi import HTTPException
import logging
from datetime import date, timedelta

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_dashboard(
    client_id: Optional[str] = None,
    date_range: str = "7d"
) -> Dict[str, Any]:
    """
    Get analytics dashboard with real Supabase data

    Args:
        client_id: Optional client UUID (if None, aggregate all clients)
        date_range: Time range (7d, 30d, 90d)

    Returns:
        Dict with content_generated, scheduled_posts, agent_executions, client_context stats

    Raises:
        HTTPException 500: Database error
    """
    try:
        supabase = get_supabase_service()

        # Calculate date range
        range_days = {"7d": 7, "30d": 30, "90d": 90}.get(date_range, 7)
        start_date = (date.today() - timedelta(days=range_days)).isoformat()
        today = date.today().isoformat()

        # 1. Content Generated Stats
        content_query = supabase.client.table("content_lab_generated")\
            .select("id, content_type, created_at")\
            .gte("created_at", f"{start_date}T00:00:00")\
            .lte("created_at", f"{today}T23:59:59")

        if client_id:
            content_query = content_query.eq("client_id", client_id)

        content_resp = content_query.execute()
        content_data = content_resp.data or []

        # Count by type
        by_type = {}
        by_day = {}
        for item in content_data:
            # By type
            ctype = item.get("content_type", "unknown")
            by_type[ctype] = by_type.get(ctype, 0) + 1

            # By day
            day = item.get("created_at", "")[:10]
            by_day[day] = by_day.get(day, 0) + 1

        # Calculate trend (compare with previous period)
        prev_start = (date.today() - timedelta(days=range_days * 2)).isoformat()
        prev_end = start_date

        prev_content_query = supabase.client.table("content_lab_generated")\
            .select("id", count="exact")\
            .gte("created_at", f"{prev_start}T00:00:00")\
            .lt("created_at", f"{prev_end}T00:00:00")

        if client_id:
            prev_content_query = prev_content_query.eq("client_id", client_id)

        prev_content_resp = prev_content_query.execute()
        prev_count = prev_content_resp.count if prev_content_resp.count else 0
        current_count = len(content_data)

        trend = 0
        if prev_count > 0:
            trend = round(((current_count - prev_count) / prev_count) * 100, 1)

        content_stats = {
            "total": current_count,
            "by_type": by_type,
            "by_day": by_day,
            "trend": trend
        }

        # 2. Scheduled Posts Stats
        posts_query = supabase.client.table("scheduled_posts")\
            .select("id, status, scheduled_date")\
            .eq("is_active", True)

        if client_id:
            posts_query = posts_query.eq("client_id", client_id)

        posts_resp = posts_query.execute()
        posts_data = posts_resp.data or []

        by_status = {}
        for post in posts_data:
            status = post.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        # Upcoming posts
        upcoming = [
            {"id": p["id"], "scheduled_date": p.get("scheduled_date")}
            for p in sorted(posts_data, key=lambda x: x.get("scheduled_date", ""))[:5]
            if p.get("scheduled_date", "") >= today
        ]

        scheduled_stats = {
            "total": len(posts_data),
            "by_status": by_status,
            "upcoming": upcoming
        }

        # 3. Agent Executions Stats
        exec_query = supabase.client.table("agent_executions")\
            .select("id, agent_id, status, execution_time_ms, started_at")\
            .gte("started_at", f"{start_date}T00:00:00")\
            .lte("started_at", f"{today}T23:59:59")

        if client_id:
            exec_query = exec_query.eq("client_id", client_id)

        exec_resp = exec_query.execute()
        exec_data = exec_resp.data or []

        successful = sum(1 for e in exec_data if e.get("status") == "completed")
        total_execs = len(exec_data)
        success_rate = round((successful / total_execs) * 100, 1) if total_execs > 0 else 0

        by_agent = {}
        total_time = 0
        for ex in exec_data:
            agent = ex.get("agent_id", "unknown")
            by_agent[agent] = by_agent.get(agent, 0) + 1
            if ex.get("execution_time_ms"):
                total_time += ex.get("execution_time_ms", 0)

        avg_time = round(total_time / total_execs, 2) if total_execs > 0 else 0

        # Top 10 agents
        top_agents = dict(sorted(by_agent.items(), key=lambda x: x[1], reverse=True)[:10])

        agent_stats = {
            "total": total_execs,
            "success_rate": success_rate,
            "by_agent": top_agents,
            "avg_execution_time_ms": avg_time
        }

        # 4. Client Context (if client_id provided)
        context_stats = {}
        if client_id:
            context_resp = supabase.client.table("client_context")\
                .select("niche, tone, updated_at")\
                .eq("client_id", client_id)\
                .limit(1)\
                .execute()

            if context_resp.data and len(context_resp.data) > 0:
                ctx = context_resp.data[0]
                context_stats = {
                    "has_context": True,
                    "last_updated": ctx.get("updated_at"),
                    "niche": ctx.get("niche"),
                    "tone": ctx.get("tone")
                }
            else:
                context_stats = {"has_context": False}

        logger.info(f"Dashboard stats: {current_count} content, {total_execs} executions")

        return {
            "content_generated": content_stats,
            "scheduled_posts": scheduled_stats,
            "agent_executions": agent_stats,
            "client_context": context_stats,
            "date_range": date_range,
            "client_id": client_id
        }

    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
