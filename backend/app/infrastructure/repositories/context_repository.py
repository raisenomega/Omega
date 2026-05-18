"""
Client Context Repository
Database operations for client context management
"""
from typing import Optional, Dict, Any
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class ContextRepository:
    """Repository for client context CRUD operations"""

    def __init__(self):
        self.service = get_supabase_service()

    async def create_client_context(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new client context profile

        Args:
            data: Context data (business_name, industry, etc.)

        Returns:
            Created context object

        Raises:
            Exception: Database error
        """
        try:
            response = self.service.client.table("client_context")\
                .insert(data)\
                .execute()

            logger.info(f"Context created for client {data.get('client_id')}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error creating client context: {e}")
            raise

    async def get_client_context(
        self,
        client_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get client context profile by client_id

        Args:
            client_id: Client UUID

        Returns:
            Context object or None if not found
        """
        try:
            response = self.service.client.table("client_context")\
                .select("*")\
                .eq("client_id", client_id)\
                .eq("is_active", True)\
                .order("version", desc=True)\
                .limit(1)\
                .execute()

            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting client context: {e}")
            raise

    async def update_client_context(
        self,
        client_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update client context profile

        Args:
            client_id: Client UUID
            data: Updated context fields

        Returns:
            Updated context object
        """
        try:
            response = self.service.client.table("client_context")\
                .update(data)\
                .eq("client_id", client_id)\
                .eq("is_active", True)\
                .execute()

            logger.info(f"Context updated for client {client_id}")
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error updating client context: {e}")
            raise

    async def get_context_for_generation(
        self,
        client_id: str
    ) -> Optional[str]:
        """
        Get AI-generated brief for content generation injection

        Args:
            client_id: Client UUID

        Returns:
            AI-generated brief string or None

        Used by content generation endpoints to inject context
        into prompts for personalized output
        """
        try:
            response = self.service.client.table("client_context")\
                .select("ai_generated_brief, custom_instructions")\
                .eq("client_id", client_id)\
                .eq("is_active", True)\
                .order("version", desc=True)\
                .limit(1)\
                .execute()

            if not response.data:
                return None

            row = response.data[0]

            # Primary: use AI-generated brief if exists
            if row.get("ai_generated_brief"):
                return row["ai_generated_brief"]

            # Fallback: use custom_instructions until brief is generated
            if row.get("custom_instructions"):
                return row["custom_instructions"]

            return None
        except Exception as e:
            logger.error(f"Error getting context for generation: {e}")
            raise


# Global instance
context_repository = ContextRepository()
