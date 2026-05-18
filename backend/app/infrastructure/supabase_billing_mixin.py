"""Stripe subscription methods for SupabaseService"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class BillingMixin:
    async def update_client_subscription(
        self,
        client_id: str,
        stripe_customer_id: str,
        stripe_subscription_id: str,
        plan: str,
        subscription_status: str = "active",
    ) -> Dict[str, Any]:
        try:
            update_data = {
                "stripe_customer_id": stripe_customer_id,
                "stripe_subscription_id": stripe_subscription_id,
                "plan": plan,
                "subscription_status": subscription_status,
                "trial_active": False,
            }
            r = self.client.table("clients").update(update_data).eq("id", client_id).execute()
            logger.info(f"Client {client_id} subscription updated: {plan} - {subscription_status}")
            return r.data[0] if r.data else {}
        except Exception as e:
            logger.error(f"Error updating client subscription: {e}")
            raise

    async def cancel_client_subscription(self, stripe_subscription_id: str) -> Dict[str, Any]:
        try:
            update_data = {"subscription_status": "cancelled", "plan": None}
            r = self.client.table("clients")\
                .update(update_data)\
                .eq("stripe_subscription_id", stripe_subscription_id)\
                .execute()
            logger.info(f"Subscription {stripe_subscription_id} marked as cancelled")
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error cancelling client subscription: {e}")
            raise

    async def get_client_subscription(self, client_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table("clients")\
                .select("id, stripe_customer_id, stripe_subscription_id, plan, subscription_status, trial_active")\
                .eq("id", client_id)\
                .execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting client subscription: {e}")
            raise

    async def get_client_by_stripe_subscription(self, stripe_subscription_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table("clients")\
                .select("*")\
                .eq("stripe_subscription_id", stripe_subscription_id)\
                .execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting client by stripe subscription: {e}")
            raise
