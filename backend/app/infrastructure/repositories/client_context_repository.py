"""
Client Context Repository
Data access layer for client context (shared memory)
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
from datetime import datetime
import logging

from app.domain.agents.context_entity import ClientContext
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class ClientContextRepository:
    """Repository for client context data operations"""

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase

    def find_by_client_id(self, client_id: str) -> Optional[ClientContext]:
        """Find context for a client"""
        response = self.supabase.client.table("client_context")\
            .select("*")\
            .eq("client_id", client_id)\
            .limit(1)\
            .execute()

        if not response.data or len(response.data) == 0:
            return None

        return self._map_to_entity(response.data[0])

    def create(self, context: ClientContext) -> ClientContext:
        """Create new client context"""
        data = {
            "client_id": context.client_id,
            "niche": context.niche,
            "tone": context.tone,
            "brand_voice": context.brand_voice,
            "target_audience": context.target_audience,
            "competitors": context.competitors,
            "best_performing_content": context.best_performing_content,
            "posting_patterns": context.posting_patterns,
            "avg_engagement_rate": context.avg_engagement_rate,
            "peak_posting_hours": context.peak_posting_hours,
            "top_hashtags": context.top_hashtags,
            "audience_demographics": context.audience_demographics,
            "content_themes": context.content_themes,
            "avoided_topics": context.avoided_topics,
            "preferred_formats": context.preferred_formats,
            "last_updated_by": context.last_updated_by,
        }

        response = self.supabase.client.table("client_context").insert(data).execute()
        return self._map_to_entity(response.data[0])

    def update(self, context: ClientContext) -> ClientContext:
        """Update existing client context"""
        data = {
            "niche": context.niche,
            "tone": context.tone,
            "brand_voice": context.brand_voice,
            "target_audience": context.target_audience,
            "competitors": context.competitors,
            "best_performing_content": context.best_performing_content,
            "posting_patterns": context.posting_patterns,
            "avg_engagement_rate": context.avg_engagement_rate,
            "peak_posting_hours": context.peak_posting_hours,
            "top_hashtags": context.top_hashtags,
            "audience_demographics": context.audience_demographics,
            "content_themes": context.content_themes,
            "avoided_topics": context.avoided_topics,
            "preferred_formats": context.preferred_formats,
            "last_updated_by": context.last_updated_by,
        }

        response = self.supabase.client.table("client_context")\
            .update(data)\
            .eq("client_id", context.client_id)\
            .execute()

        return self._map_to_entity(response.data[0])

    def upsert(self, context: ClientContext) -> ClientContext:
        """Create or update client context"""
        existing = self.find_by_client_id(context.client_id)
        if existing:
            context.id = existing.id
            return self.update(context)
        else:
            return self.create(context)

    def _map_to_entity(self, row: dict) -> ClientContext:
        """Map database row to ClientContext entity"""
        return ClientContext(
            id=row.get("id"),
            client_id=row.get("client_id", ""),
            niche=row.get("niche"),
            tone=row.get("tone"),
            brand_voice=row.get("brand_voice", {}),
            target_audience=row.get("target_audience"),
            competitors=row.get("competitors", []),
            best_performing_content=row.get("best_performing_content", []),
            posting_patterns=row.get("posting_patterns", {}),
            avg_engagement_rate=row.get("avg_engagement_rate"),
            peak_posting_hours=row.get("peak_posting_hours", []),
            top_hashtags=row.get("top_hashtags", []),
            audience_demographics=row.get("audience_demographics", {}),
            content_themes=row.get("content_themes", []),
            avoided_topics=row.get("avoided_topics", []),
            preferred_formats=row.get("preferred_formats", []),
            last_updated_by=row.get("last_updated_by"),
            created_at=self._parse_datetime(row.get("created_at")),
            updated_at=self._parse_datetime(row.get("updated_at")),
        )

    @staticmethod
    def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string"""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
