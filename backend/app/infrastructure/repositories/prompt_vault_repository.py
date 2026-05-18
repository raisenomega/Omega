"""
Prompt Vault Repository — Dynamic prompt selection with performance tracking.
DDD: Infrastructure layer - data access.
Strict <200L per file.
"""
from typing import Optional, Dict, Any, List
from app.infrastructure.supabase_service import SupabaseService
import logging

logger = logging.getLogger(__name__)


class PromptVaultRepository:
    """Repository for Prompt Vault operations"""

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    async def select_optimal_prompt(
        self, category: str, vertical: str, platform: str, agent_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        3-tier fallback: exact → vertical → generic.
        Returns best prompt by performance_score.
        """
        try:
            # Tier 1: Exact match (category + vertical + platform + agent)
            prompt = await self._try_match({
                "category": category,
                "vertical": vertical,
                "platform": platform,
                "agent_code": agent_code,
                "is_active": True
            })
            if prompt:
                logger.info(f"Exact match: {prompt['name']} (score={prompt['performance_score']})")
                await self._increment_usage(prompt["id"], prompt["times_used"])
                return prompt

            # Tier 2: Fallback without platform
            prompt = await self._try_match({
                "category": category,
                "vertical": vertical,
                "agent_code": agent_code,
                "is_active": True
            })
            if prompt:
                logger.info(f"Vertical match: {prompt['name']}")
                await self._increment_usage(prompt["id"], prompt["times_used"])
                return prompt

            # Tier 3: Generic vertical
            prompt = await self._try_match({
                "category": category,
                "vertical": "generic",
                "agent_code": agent_code,
                "is_active": True
            })
            if prompt:
                logger.info(f"Generic match: {prompt['name']}")
                await self._increment_usage(prompt["id"], prompt["times_used"])
                return prompt

            logger.warning(f"No vault prompt for {category}/{vertical}, using default")
            return None

        except Exception as e:
            logger.error(f"Error selecting prompt: {e}")
            return None

    async def _try_match(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try to find a prompt matching the given filters"""
        response = self.supabase.client.table("prompt_vault").select("*").match(
            filters
        ).order("performance_score", desc=True).limit(1).execute()
        return response.data[0] if response.data else None

    async def _increment_usage(self, prompt_id: str, current_count: int) -> None:
        """Increment times_used counter"""
        try:
            self.supabase.client.table("prompt_vault").update({
                "times_used": current_count + 1,
                "last_updated": "now()"
            }).eq("id", prompt_id).execute()
        except Exception as e:
            logger.error(f"Failed to increment usage: {e}")

    async def update_performance_score(
        self, prompt_id: str, engagement_rate: float
    ) -> None:
        """
        Updates performance_score based on engagement.
        Formula: new_score = (old * 0.7) + (engagement * 10 * 0.3)
        """
        try:
            # Get current data
            response = self.supabase.client.table("prompt_vault").select(
                "performance_score, engagement_avg, times_used"
            ).eq("id", prompt_id).execute()

            if not response.data:
                logger.warning(f"Prompt {prompt_id} not found")
                return

            current = response.data[0]
            old_score = current["performance_score"]
            times_used = current["times_used"]

            # Calculate new engagement average (running average)
            if current["engagement_avg"] is None:
                new_engagement_avg = engagement_rate
            else:
                old_avg = current["engagement_avg"]
                new_engagement_avg = (
                    (old_avg * (times_used - 1)) + engagement_rate
                ) / times_used

            # Calculate new score (weighted 70% old, 30% new)
            new_score = (old_score * 0.7) + (engagement_rate * 10 * 0.3)
            new_score = max(0.0, min(10.0, new_score))  # Clamp 0-10

            # Update database
            self.supabase.client.table("prompt_vault").update({
                "performance_score": round(new_score, 2),
                "engagement_avg": round(new_engagement_avg, 4),
                "last_updated": "now()"
            }).eq("id", prompt_id).execute()

            logger.info(
                f"Updated {prompt_id}: {old_score:.2f} → {new_score:.2f}, "
                f"engagement={new_engagement_avg:.4f}"
            )

        except Exception as e:
            logger.error(f"Error updating performance: {e}")

    async def get_top_prompts(
        self, vertical: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing prompts, optionally filtered by vertical"""
        try:
            query = self.supabase.client.table("prompt_vault").select("*").eq(
                "is_active", True
            )

            if vertical:
                query = query.eq("vertical", vertical)

            response = query.order(
                "performance_score", desc=True
            ).limit(limit).execute()

            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Error fetching top prompts: {e}")
            return []

    async def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a single prompt by ID"""
        try:
            response = self.supabase.client.table("prompt_vault").select("*").eq(
                "id", prompt_id
            ).execute()

            return response.data[0] if response.data else None

        except Exception as e:
            logger.error(f"Error fetching prompt {prompt_id}: {e}")
            return None
