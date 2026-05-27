"""GET /security-dev/sentinel · últimas 10 corridas de sentinel_risk_scores."""
import logging
from typing import Optional, Dict, Any
from app.api.routes.auth.super_owner import require_super_owner
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)

_SCORES_LIMIT = 10


async def handle_sentinel_data(authorization: Optional[str]) -> Dict[str, Any]:
    await require_super_owner(authorization)
    sb = get_supabase_service().client
    try:
        r = sb.table("sentinel_risk_scores") \
            .select(
                "id, score, security_score, architecture_score, performance_score, "
                "quality_score, deployment_score, documentation_score, "
                "verdict, issues_critical, issues_high, issues_medium, issues_low, "
                "auto_fixes_applied, calculated_at"
            ) \
            .order("calculated_at", desc=True) \
            .limit(_SCORES_LIMIT) \
            .execute()
        rows = r.data or []
        return {
            "latest":  rows[0] if rows else None,
            "history": rows,
            "count":   len(rows),
        }
    except Exception as e:
        logger.error(f"handle_sentinel_data failed: {e}", exc_info=True)
        return {"latest": None, "history": [], "count": 0, "error": str(e)}
