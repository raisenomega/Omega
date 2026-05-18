"""
Nova Repository — Data access for nova_full_context VIEW.
DDD: Infrastructure layer. Only queries — zero business logic.
Filosofía: No velocity, only precision 🐢💎

NOTE: append_learning uses RPC 'append_nova_learning' which must exist in Supabase:
  CREATE OR REPLACE FUNCTION append_nova_learning(p_client_id UUID, p_key TEXT, p_value TEXT)
  RETURNS void LANGUAGE plpgsql AS $$
  BEGIN
    UPDATE client_context
    SET nova_learnings = COALESCE(nova_learnings, '[]'::jsonb)
                         || jsonb_build_array(jsonb_build_object(p_key, p_value))
    WHERE client_id = p_client_id;
  END; $$;
"""
import json
import logging
from typing import Optional

from app.domain.nova_entities import NovaFullContext
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


class NovaRepository:
    """Repository for NOVA context. Reads nova_full_context VIEW."""

    def __init__(self, supabase: SupabaseService) -> None:
        self.supabase = supabase  # [R-DDD-001] full service stored, .client accessed internally

    def get_full_context(self, client_id: str) -> Optional[NovaFullContext]:
        """
        Fetch full client context from nova_full_context VIEW.
        Query: SELECT * FROM nova_full_context WHERE client_id = :id LIMIT 1
        """
        safe_id = client_id if client_id and str(client_id).strip() else None  # [R-UUID-002]
        if not safe_id:
            raise ValueError("client_id is required and cannot be empty")

        try:
            response = (
                self.supabase.client
                .table("nova_full_context")
                .select("*")
                .eq("client_id", safe_id)
                .limit(1)
                .execute()
            )
            if not response.data:
                return None
            return self._map_to_entity(response.data[0])
        except Exception as e:
            logger.error(f"NovaRepository.get_full_context failed [{client_id}]: {e}")
            raise

    def append_learning(self, client_id: str, key: str, value: str) -> None:
        """
        Append learning to nova_learnings JSONB array via RPC.
        Uses: nova_learnings || jsonb_build_array(jsonb_build_object(key, value))
        """
        safe_id = client_id if client_id and str(client_id).strip() else None  # [R-UUID-002]
        if not safe_id:
            raise ValueError("client_id is required and cannot be empty")
        safe_key = key if key and str(key).strip() else None
        if not safe_key:
            raise ValueError("learning_key is required and cannot be empty")

        try:
            self.supabase.client.rpc(
                "append_nova_learning",
                {"p_client_id": safe_id, "p_key": safe_key, "p_value": value},
            ).execute()
        except Exception as e:
            logger.error(f"NovaRepository.append_learning failed [{client_id}]: {e}")
            raise

    def update_context_fields(self, client_id: str, fields: dict[str, str]) -> None:
        """Update specific fields in client_context table (only non-None values)."""
        safe_id = client_id if client_id and str(client_id).strip() else None  # [R-UUID-002]
        if not safe_id:
            raise ValueError("client_id is required and cannot be empty")
        if not fields:
            return

        try:
            (
                self.supabase.client
                .table("client_context")
                .update(fields)
                .eq("client_id", safe_id)
                .execute()
            )
        except Exception as e:
            logger.error(f"NovaRepository.update_context_fields failed [{client_id}]: {e}")
            raise

    # ─── Private helpers ──────────────────────────────────────────────────────

    def _map_to_entity(self, row: dict) -> NovaFullContext:
        """Map nova_full_context VIEW row to NovaFullContext entity."""
        return NovaFullContext(
            client_id=str(row.get("client_id", "")),
            client_name=str(row.get("client_name") or row.get("name") or ""),
            nova_tier=str(row.get("nova_tier") or "sistema_only"),
            company_agents=self._to_list_str(row.get("company_agents")),
            onboarding_active=bool(row.get("onboarding_active", False)),
            niche=self._safe_str(row.get("niche")),
            tone=self._safe_str(row.get("tone")),
            business_what=self._safe_str(row.get("business_what")),
            business_to_whom=self._safe_str(row.get("business_to_whom")),
            business_diff=self._safe_str(row.get("business_diff")),
            business_geo=self._safe_str(row.get("business_geo")),
            target_audience=self._safe_str(row.get("target_audience")),
            brand_voice=self._to_dict_str(row.get("brand_voice")),
            brand_file=self._to_dict_str(row.get("brand_file")),
            goal_this_month=self._safe_str(row.get("goal_this_month")),
            goal_this_quarter=self._safe_str(row.get("goal_this_quarter")),
            goal_priority_now=self._safe_str(row.get("goal_priority_now")),
            what_worked=self._safe_str(row.get("what_worked")),
            what_failed=self._safe_str(row.get("what_failed")),
            nova_learnings=self._to_list_dict_str(row.get("nova_learnings")),
            nova_can_publish=self._to_list_str(row.get("nova_can_publish")),
            custom_instructions=self._safe_str(row.get("custom_instructions")),
            competitors=self._to_list_str(row.get("competitors")),
            content_themes=self._to_list_str(row.get("content_themes")),
            posting_patterns=self._to_dict_str(row.get("posting_patterns")),
            avg_engagement_rate=(
                float(row["avg_engagement_rate"])
                if row.get("avg_engagement_rate") is not None else None
            ),
            top_hashtags=self._to_list_str(row.get("top_hashtags")),
            avoided_topics=self._to_list_str(row.get("avoided_topics")),
            preferred_formats=self._to_list_str(row.get("preferred_formats")),
            onboarding_complete=bool(row.get("onboarding_complete", False)),
        )

    @staticmethod
    def _safe_str(val: object) -> Optional[str]:
        """Return stripped string or None. Never returns empty string."""
        if val is None:
            return None
        stripped = str(val).strip()
        return stripped if stripped else None

    @staticmethod
    def _to_list_str(val: object) -> list[str]:
        """Parse to list[str]. Handles: None → [], list, JSON-encoded string."""
        if val is None:
            return []
        if isinstance(val, list):
            return [str(item) for item in val if item is not None]
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed if item is not None]
            except (json.JSONDecodeError, ValueError):
                pass
        return []

    @staticmethod
    def _to_dict_str(val: object) -> dict[str, str]:
        """Parse to dict[str, str]. Handles: None → {}, dict, JSON-encoded string."""
        if val is None:
            return {}
        if isinstance(val, dict):
            return {str(k): str(v) for k, v in val.items() if v is not None}
        if isinstance(val, str):
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items() if v is not None}
            except (json.JSONDecodeError, ValueError):
                pass
        return {}

    @staticmethod
    def _to_list_dict_str(val: object) -> list[dict[str, str]]:
        """Parse to list[dict[str,str]]. Handles: None → [], list, JSON-encoded string."""
        if val is None:
            return []
        raw = val
        if isinstance(val, str):
            try:
                raw = json.loads(val)
            except (json.JSONDecodeError, ValueError):
                return []
        if not isinstance(raw, list):
            return []
        result: list[dict[str, str]] = []
        for item in raw:
            if isinstance(item, dict):
                result.append({str(k): str(v) for k, v in item.items()})
        return result
