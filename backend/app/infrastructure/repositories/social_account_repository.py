"""
Social Account Repository
Database operations for social account management
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import logging
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class SocialAccountRepository:
    """Repository for social account CRUD operations"""

    def __init__(self):
        self.service = get_supabase_service()

    async def list_accounts(
        self,
        client_id: str,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List social accounts for a client with optional platform filter.

        Args:
            client_id: Client UUID
            platform: Optional platform filter

        Returns:
            List of social account dicts
        """
        try:
            query = self.service.client.table("social_accounts")\
                .select("*")\
                .eq("client_id", client_id)\
                .eq("is_active", True)

            if platform:
                query = query.eq("platform", platform)

            query = query.order("created_at", desc=True)

            response = query.execute()
            accounts_data = response.data if response.data else []

            return accounts_data

        except Exception as e:
            logger.error(f"Error listing social accounts: {e}")
            raise

    async def create_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new social account.

        Args:
            data: Account data dict

        Returns:
            Created account dict
        """
        try:
            response = self.service.client.table("social_accounts")\
                .insert(data)\
                .execute()

            if not response.data or len(response.data) == 0:
                raise Exception("Failed to create social account")

            account = response.data[0]
            logger.info(
                f"Social account created: {account.get('platform')} - "
                f"{account.get('username')} for client {data.get('client_id')}"
            )
            return account

        except Exception as e:
            logger.error(f"Error creating social account: {e}")
            raise

    async def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Get social account by ID.

        Args:
            account_id: Account UUID

        Returns:
            Account dict or None if not found
        """
        try:
            response = self.service.client.table("social_accounts")\
                .select("*")\
                .eq("id", account_id)\
                .eq("is_active", True)\
                .execute()

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error getting social account: {e}")
            raise

    async def update_account(
        self,
        account_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update social account fields.

        Args:
            account_id: Account UUID
            data: Update data dict

        Returns:
            Updated account dict
        """
        try:
            data["updated_at"] = datetime.now(timezone.utc).isoformat()

            response = self.service.client.table("social_accounts")\
                .update(data)\
                .eq("id", account_id)\
                .execute()

            if not response.data or len(response.data) == 0:
                raise Exception("Social account not found or update failed")

            account = response.data[0]
            logger.info(f"Social account updated: {account_id}")
            return account

        except Exception as e:
            logger.error(f"Error updating social account: {e}")
            raise

    async def delete_account(self, account_id: str) -> bool:
        """
        Soft delete: is_active = false.

        Args:
            account_id: Account UUID

        Returns:
            True if deleted successfully
        """
        try:
            response = self.service.client.table("social_accounts")\
                .update({
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                })\
                .eq("id", account_id)\
                .execute()

            if not response.data or len(response.data) == 0:
                return False

            logger.info(f"Social account soft deleted: {account_id}")
            return True

        except Exception as e:
            logger.error(f"Error soft deleting social account: {e}")
            raise


# Global instance
social_account_repository = SocialAccountRepository()
