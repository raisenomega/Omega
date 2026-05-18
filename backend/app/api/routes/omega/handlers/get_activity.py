"""
Handler: Recent Activity Feed
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any, List
from fastapi import HTTPException
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def handle_get_activity(limit: int = 50) -> Dict[str, Any]:
    """
    Get recent activity feed from multiple tables

    Args:
        limit: Number of activity items to return

    Returns:
        Dict with activity feed items
    """
    try:
        supabase = get_supabase_service()
        activities = []

        # 1. Recent content generated
        content_resp = supabase.client.table("content_lab_generated")\
            .select("id, content_type, provider, created_at, client_id")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        for item in (content_resp.data or []):
            activities.append({
                "type": "content_generated",
                "description": f"Generated {item.get('content_type')} via {item.get('provider')}",
                "timestamp": item.get("created_at"),
                "client_id": item.get("client_id")
            })

        # 2. Recent agent executions
        exec_resp = supabase.client.table("agent_executions")\
            .select("id, agent_id, status, started_at, client_id")\
            .order("started_at", desc=True)\
            .limit(20)\
            .execute()

        for item in (exec_resp.data or []):
            activities.append({
                "type": "agent_execution",
                "description": f"Agent '{item.get('agent_id')}' executed ({item.get('status')})",
                "timestamp": item.get("started_at"),
                "client_id": item.get("client_id")
            })

        # 3. Recent posts scheduled
        posts_resp = supabase.client.table("scheduled_posts")\
            .select("id, status, scheduled_date, created_at, client_id, agent_assigned, account_id")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        for item in (posts_resp.data or []):
            activities.append({
                "type": "post_scheduled",
                "description": f"Post programado {item.get('scheduled_date', '')[:10]}",
                "agent_code": item.get("agent_assigned", "DUDA"),
                "timestamp": item.get("created_at"),
                "client_id": item.get("client_id"),
                "status": item.get("status")
            })

        # 4. Recent agent tasks
        tasks_resp = supabase.client.table("agent_tasks")\
            .select("id, agent_code, title, status, client_id, tokens_used, provider, created_at, completed_at")\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        for item in (tasks_resp.data or []):
            activities.append({
                "type": "agent_task",
                "description": f"{item.get('agent_code')} — {item.get('title', '')[:80]}",
                "agent_code": item.get("agent_code"),
                "status": item.get("status"),
                "timestamp": item.get("created_at"),
                "client_id": item.get("client_id"),
                "tokens_used": item.get("tokens_used", 0),
                "provider": item.get("provider", "")
            })

        # Sort all activities by timestamp and limit
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        activities = activities[:limit]

        logger.info(f"Retrieved {len(activities)} activity items")

        return {
            "activities": activities,
            "total": len(activities)
        }

    except Exception as e:
        logger.error(f"Error getting activity feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activity: {str(e)}")
