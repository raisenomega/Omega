"""Handler: última auditoría RLS para el panel · owner-only."""
from typing import Dict, Any, Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin


async def handle_rls_audit_status(authorization: Optional[str]) -> Dict[str, Any]:
    """Devuelve la última fila de sentinel_rls_audits (con issues jsonb)."""
    await require_superadmin(authorization)
    supabase = get_supabase_service()
    resp = supabase.client.table("sentinel_rls_audits")\
        .select("*").order("created_at", desc=True).limit(1).execute()
    return {"latest": (resp.data or [None])[0]}
