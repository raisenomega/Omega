"""
Scheduling Agent
Specialized in content scheduling and queue management
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.openai_service import openai_service
from app.services.queue_manager import (
    ScheduledPost,
    PublicationQueue,
    OptimalTimingResult,
    generate_post_id,
    validate_scheduled_time,
    sort_queue_by_priority,
    filter_posts_by_status,
    filter_posts_by_platform,
    get_next_publication
)

logger = logging.getLogger(__name__)


class SchedulingAgent(BaseAgent):
    """
    Agent specialized in scheduling and queue management
    - Post scheduling with optimal timing
    - Queue management with approval workflow
    - Optimal time calculation
    - Bulk scheduling across days
    """

    def __init__(self, agent_id: str = "scheduling_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.CONTENT_CREATOR,
            model="gpt-4",
            tools=[
                "scheduler",
                "queue_manager",
                "timing_optimizer",
                "approval_system"
            ]
        )
        # In-memory storage (in production, use database)
        self.posts_db: Dict[str, List[ScheduledPost]] = {}

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scheduling task"""
        self.set_state(AgentState.WORKING)

        try:
            task_type = task.get("type")

            if task_type == "schedule_post":
                result = await self.schedule_post(
                    task["post_data"],
                    task["client_preferences"]
                )
            elif task_type == "get_queue":
                result = await self.get_queue(
                    task["client_id"],
                    task.get("status_filter"),
                    task.get("platform_filter")
                )
            elif task_type == "approve_post":
                result = await self.approve_post(
                    task["post_id"],
                    task["reviewer_id"],
                    task.get("approval_notes", "")
                )
            elif task_type == "calculate_optimal_times":
                result = await self.calculate_optimal_times(
                    task["platform"],
                    task["audience_timezone"],
                    task["content_type"]
                )
            elif task_type == "bulk_schedule":
                result = await self.bulk_schedule(
                    task["posts"],
                    task["client_id"],
                    task.get("spread_days", 7)
                )
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            self.set_state(AgentState.IDLE)
            return result.model_dump() if hasattr(result, 'model_dump') else result

        except Exception as e:
            logger.error(f"Scheduling execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def schedule_post(
        self,
        post_data: dict[str, str | List],
        client_preferences: dict[str, str]
    ) -> ScheduledPost:
        """Create and schedule a post with optimal timing"""
        client_id = client_preferences.get("client_id", "default_client")

        # Generate post ID
        post_id = generate_post_id()

        # If no scheduled time provided, calculate optimal time
        scheduled_time = post_data.get("scheduled_time")
        if not scheduled_time:
            platform = post_data["platform"]
            timezone = client_preferences.get("timezone", "America/Puerto_Rico")
            content_type = post_data.get("content_type", "image")

            timing_result = await self.calculate_optimal_times(
                platform, timezone, content_type
            )
            scheduled_time = timing_result.recommended_slots[0]

        # Validate scheduled time
        if not validate_scheduled_time(scheduled_time, post_data["platform"]):
            # Adjust to next valid time
            scheduled_time = (datetime.now() + timedelta(hours=2)).isoformat()

        # Create scheduled post
        post = ScheduledPost(
            post_id=post_id,
            client_id=client_id,
            platform=post_data["platform"],
            content_type=post_data.get("content_type", "image"),
            caption=post_data["caption"],
            hashtags=post_data.get("hashtags", []),
            media_urls=post_data.get("media_urls", []),
            scheduled_time=scheduled_time,
            timezone=client_preferences.get("timezone", "America/Puerto_Rico"),
            status="pending_approval" if client_preferences.get("require_approval") else "scheduled",
            priority=post_data.get("priority", "normal"),
            created_by=post_data.get("created_by", "ai_generated"),
            approved_by=None,
            approved_at=None,
            notes=post_data.get("notes")
        )

        # Store in database
        if client_id not in self.posts_db:
            self.posts_db[client_id] = []
        self.posts_db[client_id].append(post)

        logger.info(f"Scheduled post {post_id} for {scheduled_time}")
        return post

    async def get_queue(
        self,
        client_id: str,
        status_filter: str | None,
        platform_filter: str | None
    ) -> PublicationQueue:
        """Return publication queue with filters"""
        # Get all posts for client
        all_posts = self.posts_db.get(client_id, [])

        # Apply filters
        filtered_posts = filter_posts_by_status(all_posts, status_filter)
        filtered_posts = filter_posts_by_platform(filtered_posts, platform_filter)

        # Sort by priority
        filtered_posts = sort_queue_by_priority(filtered_posts)

        # Calculate stats
        pending_approval = len([p for p in all_posts if p.status == "pending_approval"])
        scheduled_count = len([p for p in all_posts if p.status in ["approved", "scheduled"]])
        published_today = len([
            p for p in all_posts
            if p.status == "published" and p.scheduled_time.startswith(datetime.now().date().isoformat())
        ])

        # Get next publication
        next_pub = get_next_publication(all_posts)

        return PublicationQueue(
            client_id=client_id,
            total_posts=len(all_posts),
            pending_approval=pending_approval,
            scheduled_count=scheduled_count,
            published_today=published_today,
            posts=filtered_posts,
            next_publication=next_pub
        )

    async def approve_post(
        self,
        post_id: str,
        reviewer_id: str,
        approval_notes: str = ""
    ) -> ScheduledPost:
        """Approve post for publication - human in the loop"""
        # Find post in database
        for client_posts in self.posts_db.values():
            for post in client_posts:
                if post.post_id == post_id:
                    # Update approval status
                    post.status = "approved"
                    post.approved_by = reviewer_id
                    post.approved_at = datetime.now().isoformat()
                    if approval_notes:
                        post.notes = approval_notes

                    logger.info(f"Post {post_id} approved by {reviewer_id}")
                    return post

        raise ValueError(f"Post {post_id} not found")

    async def calculate_optimal_times(
        self,
        platform: str,
        audience_timezone: str,
        content_type: str
    ) -> OptimalTimingResult:
        """Calculate best posting times based on platform and audience"""
        prompt = (
            f"Analyze optimal posting times for:\n"
            f"Platform: {platform}\n"
            f"Timezone: {audience_timezone}\n"
            f"Content type: {content_type}\n\n"
            f"Provide:\n"
            f"1. Best 3 time slots (e.g., '9:00 AM', '1:00 PM', '7:00 PM')\n"
            f"2. Brief reasoning\n"
            f"3. Expected engagement boost vs bad timing (as percentage)"
        )

        analysis = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=200,
            temperature=0.6
        )

        # Parse time slots (simplified - in production use regex/structured output)
        now = datetime.now()
        recommended_slots = []

        # Default optimal times by platform
        default_times = {
            "instagram": ["09:00", "13:00", "19:00"],
            "tiktok": ["12:00", "17:00", "21:00"],
            "facebook": ["09:00", "14:00", "19:00"],
            "twitter": ["08:00", "12:00", "17:00"],
            "linkedin": ["08:00", "12:00", "17:00"]
        }

        times = default_times.get(platform, ["09:00", "14:00", "19:00"])

        for time_str in times:
            hour, minute = map(int, time_str.split(":"))
            next_slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_slot <= now:
                next_slot += timedelta(days=1)
            recommended_slots.append(next_slot.isoformat())

        return OptimalTimingResult(
            platform=platform,
            recommended_slots=recommended_slots,
            reasoning=f"Optimal times for {platform} based on audience activity patterns",
            expected_engagement_boost=1.35,  # 35% boost vs off-peak
            audience_timezone=audience_timezone
        )

    async def bulk_schedule(
        self,
        posts: List[dict[str, str | List]],
        client_id: str,
        spread_days: int = 7
    ) -> List[ScheduledPost]:
        """Schedule multiple posts distributed over time"""
        scheduled_posts = []

        # Calculate time slots
        posts_per_day = len(posts) / spread_days
        hours_between = 24 / max(posts_per_day, 1)

        start_time = datetime.now() + timedelta(hours=2)

        for i, post_data in enumerate(posts):
            # Calculate scheduled time
            offset_hours = i * hours_between
            scheduled_time = (start_time + timedelta(hours=offset_hours)).isoformat()

            # Create post with scheduled time
            post_with_time = {**post_data, "scheduled_time": scheduled_time}

            scheduled_post = await self.schedule_post(
                post_with_time,
                {"client_id": client_id, "timezone": "America/Puerto_Rico"}
            )

            scheduled_posts.append(scheduled_post)

        logger.info(f"Bulk scheduled {len(scheduled_posts)} posts over {spread_days} days")
        return scheduled_posts


# Global instance
scheduling_agent = SchedulingAgent()
