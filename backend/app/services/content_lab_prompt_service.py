"""
Content Lab Prompt Service — Intelligent prompt selection (vault vs default).
DDD: Application Service layer - orchestrates prompt selection strategy.
Strict <200L per file.
"""
from typing import Dict, Any, Optional, Tuple
from app.infrastructure.supabase_service import SupabaseService
from app.infrastructure.repositories.prompt_vault_repository import PromptVaultRepository
from app.api.routes.content_lab.builders.prompt_builder import (
    build_user_prompt, build_system_prompt
)
import logging

logger = logging.getLogger(__name__)


class ContentLabPromptService:
    """
    Selects optimal prompt using 3-tier fallback:
    1. Try Prompt Vault (performance-tested prompts)
    2. Fallback to default prompt builder
    """

    def __init__(self, supabase: SupabaseService):
        self.supabase = supabase
        self.vault_repo = PromptVaultRepository(supabase)

    async def select_and_build_prompts(
        self,
        content_type: str,
        vertical: str,
        platform: str,
        brief: str,
        client_name: str,
        audience: str,
        tone: str,
        language: str,
        goal: str,
        context_data: Dict[str, Any],
        brand_voice: Optional[str],
        keywords: list
    ) -> Tuple[str, str, Optional[Dict[str, Any]]]:
        """
        Selects optimal prompt and builds user + system prompts.

        Returns:
            Tuple of (user_prompt, system_prompt, vault_metadata)
        """
        # Query Prompt Vault
        vault_prompt = await self.vault_repo.select_optimal_prompt(
            category=content_type,
            vertical=vertical,
            platform=platform,
            agent_code="RAFA"  # Content Lab uses RAFA
        )

        vault_used = None

        # Build user prompt (vault or default)
        if vault_prompt:
            user_prompt, vault_used = self._build_from_vault(
                vault_prompt=vault_prompt,
                brief=brief,
                platform=platform,
                audience=audience,
                tone=tone,
                client_name=client_name,
                language=language,
                goal=goal,
                content_type=content_type
            )
        else:
            user_prompt = self._build_default_prompt(
                content_type=content_type,
                brief=brief,
                platform=platform,
                audience=audience,
                tone=tone,
                goal=goal
            )
            logger.info("No vault prompt found, using default prompt builder")

        # Build system prompt (always use default builder)
        system_prompt = build_system_prompt(
            client_name=client_name,
            business_type=context_data.get("business_type"),
            brand_voice=brand_voice,
            keywords=keywords
        )

        return user_prompt, system_prompt, vault_used

    def _build_from_vault(
        self,
        vault_prompt: Dict[str, Any],
        brief: str,
        platform: str,
        audience: str,
        tone: str,
        client_name: str,
        language: str,
        goal: str,
        content_type: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Builds prompt from vault template with placeholders.

        Falls back to default if placeholder missing.
        """
        try:
            user_prompt = vault_prompt["prompt_text"].format(
                brief=brief,
                platform=platform,
                audience=audience,
                tone=tone,
                client_name=client_name,
                language=language,
                goal=goal
            )

            vault_used = {
                "id": vault_prompt["id"],
                "name": vault_prompt["name"],
                "technique": vault_prompt["technique"],
                "performance_score": vault_prompt["performance_score"]
            }

            logger.info(
                f"Using vault prompt '{vault_prompt['name']}' "
                f"(technique={vault_prompt['technique']}, "
                f"score={vault_prompt['performance_score']})"
            )

            return user_prompt, vault_used

        except KeyError as e:
            logger.warning(
                f"Vault prompt missing placeholder {e}, falling back to default"
            )
            user_prompt = self._build_default_prompt(
                content_type=content_type,
                brief=brief,
                platform=platform,
                audience=audience,
                tone=tone,
                goal=goal
            )
            return user_prompt, None

    def _build_default_prompt(
        self,
        content_type: str,
        brief: str,
        platform: str,
        audience: str,
        tone: str,
        goal: str
    ) -> str:
        """Builds prompt using default prompt builder"""
        return build_user_prompt(
            content_type=content_type,
            brief=brief,
            platform=platform,
            audience=audience,
            tone=tone,
            goal=goal
        )
