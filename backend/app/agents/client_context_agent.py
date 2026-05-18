"""
Client Context Agent
Analyzes client data and builds shared context for all agents
Filosofía: No velocity, only precision 🐢💎
"""
import logging
from typing import Optional
import json

from app.infrastructure.supabase_service import get_supabase_service
from app.infrastructure.repositories.client_context_repository import ClientContextRepository
from app.domain.agents.context_entity import ClientContext
from app.services.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class ClientContextAgent:
    """
    Agent that builds and maintains client context from all available data.
    This context is shared across all other agents for personalized outputs.
    """

    def __init__(self):
        self.supabase = get_supabase_service()
        self.context_repo = ClientContextRepository(self.supabase)
        self.llm_router = LLMRouter()

    async def execute(self, client_id: str) -> dict:
        """
        Analyze client data and build comprehensive context

        Args:
            client_id: Client UUID

        Returns:
            dict with complete client context
        """
        try:
            # 1. Gather client data
            client_data = await self._gather_client_data(client_id)

            if not client_data["client"]:
                return {
                    "error": "Client not found",
                    "client_id": client_id
                }

            # 2. Analyze with GPT-4o
            analysis = await self._analyze_with_llm(client_data)

            # 3. Save to client_context
            context = await self._save_context(client_id, analysis)

            logger.info(f"ClientContextAgent: Context built for client {client_id}")

            return {
                "client_id": client_id,
                "context": {
                    "niche": context.niche,
                    "tone": context.tone,
                    "brand_voice": context.brand_voice,
                    "target_audience": context.target_audience,
                    "content_themes": context.content_themes,
                    "preferred_formats": context.preferred_formats,
                },
                "message": "Client context updated successfully"
            }

        except Exception as e:
            logger.error(f"ClientContextAgent failed: {e}")
            return {
                "error": str(e),
                "client_id": client_id
            }

    async def _gather_client_data(self, client_id: str) -> dict:
        """Gather all available client data"""
        # Get client info
        client_resp = self.supabase.client.table("clients")\
            .select("*")\
            .eq("id", client_id)\
            .limit(1)\
            .execute()

        # Get social accounts
        accounts_resp = self.supabase.client.table("social_accounts")\
            .select("*")\
            .eq("client_id", client_id)\
            .eq("is_active", True)\
            .execute()

        # Get recent generated content
        content_resp = self.supabase.client.table("content_lab_generated")\
            .select("content_type, content, provider")\
            .eq("client_id", client_id)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        # Get scheduled posts
        posts_resp = self.supabase.client.table("scheduled_posts")\
            .select("content_type, text_content, hashtags")\
            .eq("client_id", client_id)\
            .eq("is_active", True)\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()

        return {
            "client": client_resp.data[0] if client_resp.data else None,
            "social_accounts": accounts_resp.data or [],
            "recent_content": content_resp.data or [],
            "scheduled_posts": posts_resp.data or []
        }

    async def _analyze_with_llm(self, data: dict) -> dict:
        """Analyze client data with GPT-4o"""
        prompt = self._build_analysis_prompt(data)

        response = await self.llm_router.route(
            prompt=prompt,
            tier="premium",
            response_format="json_object"
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to basic extraction
            return self._extract_basic_context(data)

    def _build_analysis_prompt(self, data: dict) -> str:
        """Build LLM prompt for context analysis"""
        client = data["client"]
        content = data["recent_content"]
        posts = data["scheduled_posts"]

        return f"""Analyze this client's social media presence and extract key context.

CLIENT INFO:
- Name: {client.get('name', 'N/A')}
- Company: {client.get('company', 'N/A')}

RECENT CONTENT ({len(content)} pieces):
{json.dumps(content[:5], indent=2)}

SCHEDULED POSTS ({len(posts)} posts):
{json.dumps(posts[:5], indent=2)}

Extract and return a JSON object with:
{{
  "niche": "Primary niche/industry (1-3 words)",
  "tone": "Communication tone (professional/casual/friendly/authoritative)",
  "brand_voice": {{
    "adjectives": ["word1", "word2", "word3"],
    "keywords": ["key1", "key2", "key3"],
    "style": "description of writing style"
  }},
  "target_audience": "Who is the target audience (be specific)",
  "content_themes": ["theme1", "theme2", "theme3"],
  "preferred_formats": ["format1", "format2"],
  "avoided_topics": []
}}

Be concise and data-driven."""

    def _extract_basic_context(self, data: dict) -> dict:
        """Fallback: Extract basic context without LLM"""
        client = data["client"]
        return {
            "niche": client.get("company", "general"),
            "tone": "professional",
            "brand_voice": {},
            "target_audience": "general audience",
            "content_themes": [],
            "preferred_formats": ["post"],
            "avoided_topics": []
        }

    async def _save_context(self, client_id: str, analysis: dict) -> ClientContext:
        """Save analysis to client_context table"""
        context = self.context_repo.find_by_client_id(client_id)

        if not context:
            context = ClientContext(client_id=client_id)

        # Update fields
        context.niche = analysis.get("niche")
        context.tone = analysis.get("tone")
        context.brand_voice = analysis.get("brand_voice", {})
        context.target_audience = analysis.get("target_audience")
        context.content_themes = analysis.get("content_themes", [])
        context.preferred_formats = analysis.get("preferred_formats", [])
        context.avoided_topics = analysis.get("avoided_topics", [])
        context.last_updated_by = "client_context"

        return self.context_repo.upsert(context)
