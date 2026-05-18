"""Reseller-domain methods for SupabaseService"""
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class ResellerMixin:
    # ── Resellers ──────────────────────────────────────────────

    async def create_reseller(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.client.table('resellers').insert(data).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error creating reseller: {e}")
            raise

    async def get_reseller(self, reseller_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table('resellers').select('*').eq('id', reseller_id).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting reseller: {e}")
            raise

    async def get_reseller_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table('resellers').select('*').eq('slug', slug).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting reseller by slug: {e}")
            raise

    async def get_all_resellers(self) -> List[Dict[str, Any]]:
        try:
            r = self.client.table('resellers').select('*').order('created_at', desc=True).execute()
            return r.data if r.data else []
        except Exception as e:
            logger.error(f"Error getting all resellers: {e}")
            raise

    async def update_reseller(self, reseller_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.client.table('resellers').update(data).eq('id', reseller_id).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error updating reseller: {e}")
            raise

    # ── Reseller Branding ──────────────────────────────────────

    async def create_branding(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.client.table('reseller_branding').insert(data).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error creating branding: {e}")
            raise

    async def get_branding(self, reseller_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table('reseller_branding').select('*').eq('reseller_id', reseller_id).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting branding: {e}")
            raise

    async def update_branding(self, reseller_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            existing = await self.get_branding(reseller_id)
            if existing:
                r = self.client.table('reseller_branding').update(data).eq('reseller_id', reseller_id).execute()
            else:
                data['reseller_id'] = reseller_id
                r = self.client.table('reseller_branding').insert(data).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error updating branding: {e}")
            raise

    # ── Reseller Agents ────────────────────────────────────────

    async def create_reseller_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.client.table('reseller_agents').insert(data).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error creating reseller agent: {e}")
            raise

    async def get_reseller_agents(self, reseller_id: str) -> List[Dict[str, Any]]:
        try:
            r = self.client.table('reseller_agents').select('*').eq('reseller_id', reseller_id).eq('status', 'active').execute()
            return r.data if r.data else []
        except Exception as e:
            logger.error(f"Error getting reseller agents: {e}")
            raise

    # ── Clients ────────────────────────────────────────────────

    async def get_reseller_clients(self, reseller_id: str) -> List[Dict[str, Any]]:
        try:
            r = self.client.table('clients').select('*').eq('reseller_id', reseller_id).execute()
            return r.data if r.data else []
        except Exception as e:
            logger.error(f"Error getting reseller clients: {e}")
            raise

    async def assign_client_to_reseller(self, client_id: str, reseller_id: str) -> Dict[str, Any]:
        try:
            r = self.client.table('clients').update({'reseller_id': reseller_id}).eq('id', client_id).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error assigning client to reseller: {e}")
            raise
