"""
Supabase Service
Handles Supabase database and storage operations.
Methods are organized in domain mixins — see:
  supabase_reseller_mixin.py  — resellers, branding, agents, clients
  supabase_leads_mixin.py     — leads, storage, user_roles
  supabase_billing_mixin.py   — Stripe subscription
"""
import logging
from supabase import create_client, Client
from app.config import settings
from .supabase_reseller_mixin import ResellerMixin
from .supabase_leads_mixin import LeadsMixin
from .supabase_billing_mixin import BillingMixin

logger = logging.getLogger(__name__)


class SupabaseService(ResellerMixin, LeadsMixin, BillingMixin):
    """Service for Supabase operations"""

    def __init__(self):
        try:
            self.client: Client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_service_role_key,
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise


# Global instance (lazy initialization)
supabase_service = None


def get_supabase_service() -> SupabaseService:
    """
    Get Supabase service instance (lazy initialization).
    Errors only affect endpoints that actually use Supabase.
    """
    global supabase_service
    if supabase_service is None:
        supabase_service = SupabaseService()
    return supabase_service
