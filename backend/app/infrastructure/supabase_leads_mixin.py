"""Leads, storage and user-roles methods for SupabaseService"""
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class LeadsMixin:
    # ── Storage ────────────────────────────────────────────────

    async def upload_media(self, bucket: str, file_path: str, file_data: bytes, content_type: str) -> str:
        try:
            self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": content_type, "upsert": "true"},
            )
            public_url = self.client.storage.from_(bucket).get_public_url(file_path)
            logger.info(f"Media uploaded: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            raise

    async def delete_media(self, bucket: str, file_path: str) -> bool:
        try:
            self.client.storage.from_(bucket).remove([file_path])
            logger.info(f"Media deleted: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting media: {e}")
            raise

    # ── Leads ──────────────────────────────────────────────────

    async def create_lead(self, data: dict) -> dict:
        try:
            r = self.client.table("leads").insert(data).execute()
            logger.info(f"Lead created for reseller {data.get('reseller_id')}")
            return r.data[0] if r.data else {}
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            raise

    async def get_reseller_leads(
        self,
        reseller_id: str,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[List[Dict[str, Any]], int]:
        try:
            query = self.client.table("leads").select("*", count="exact").eq("reseller_id", reseller_id)
            if status:
                query = query.eq("status", status)
            offset = (page - 1) * limit
            r = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return (r.data or []), (r.count if hasattr(r, "count") else 0)
        except Exception as e:
            logger.error(f"Error getting reseller leads: {e}")
            raise

    async def get_platform_leads(
        self,
        audience: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[List[Dict[str, Any]], int]:
        """Leads de PLATAFORMA (reseller_id IS NULL · landing OMEGA) · super_owner only (guard en el router)."""
        try:
            query = self.client.table("leads").select("*", count="exact").is_("reseller_id", "null")
            if audience:
                query = query.eq("audience", audience)
            if status:
                query = query.eq("status", status)
            offset = (page - 1) * limit
            r = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return (r.data or []), (r.count if hasattr(r, "count") else 0)
        except Exception as e:
            logger.error(f"Error getting platform leads: {e}")
            raise

    async def get_lead_counts(self, reseller_id: str) -> Dict[str, int]:
        try:
            r = self.client.table("leads").select("status").eq("reseller_id", reseller_id).execute()
            leads = r.data or []
            return {
                "total": len(leads),
                "new": sum(1 for l in leads if l.get("status") == "new"),
                "contacted": sum(1 for l in leads if l.get("status") == "contacted"),
                "converted": sum(1 for l in leads if l.get("status") == "converted"),
                "lost": sum(1 for l in leads if l.get("status") == "lost"),
            }
        except Exception as e:
            logger.error(f"Error getting lead counts: {e}")
            raise

    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = self.client.table("leads").select("*").eq("id", lead_id).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting lead by ID: {e}")
            raise

    async def update_lead_status(self, lead_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        try:
            update_data: Dict[str, Any] = {"status": status}
            if notes:
                update_data["notes"] = notes
            if status == "contacted":
                update_data["contacted_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "converted":
                lead = await self.get_lead_by_id(lead_id)
                if lead and not lead.get("contacted_at"):
                    update_data["contacted_at"] = datetime.now(timezone.utc).isoformat()
            r = self.client.table("leads").update(update_data).eq("id", lead_id).execute()
            logger.info(f"Lead {lead_id} status updated to {status}")
            return r.data[0] if r.data else {}
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            raise

    # ── User Roles ─────────────────────────────────────────────

    async def get_user_by_email(self, email: str) -> dict:
        try:
            r = self.client.table("user_roles").select("*").eq("email", email).execute()
            return r.data[0] if r.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise

    async def create_user_role(self, data: dict) -> dict:
        try:
            r = self.client.table("user_roles").upsert(data, on_conflict="email").execute()
            logger.info(f"User role created/updated: {data.get('email')}")
            return r.data[0] if r.data else {}
        except Exception as e:
            logger.error(f"Error creating user role: {e}")
            raise
