"""
OMEGA · GET /api/v1/feature-usage/{client_id}/
Retorna el uso real de mensajes NOVA y posts del mes actual
R-LINES-001: < 200L
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from app.api.routes.auth.auth_utils import get_current_user
from app.infrastructure.supabase_service import get_supabase_service

PLAN_LIMITS: dict[str, dict] = {
    "basic":      {"posts": 50,  "msgs": 250},
    "pro":        {"posts": 150, "msgs": 600},
    "enterprise": {"posts": None, "msgs": None},
}

router = APIRouter(prefix="/feature-usage", tags=["feature-usage"])


class FeatureUsageData(BaseModel):
    client_id: str
    plan: str
    posts_used: int
    posts_limit: Optional[int]
    posts_pct: Optional[float]
    msgs_used: int
    msgs_limit: Optional[int]
    msgs_pct: Optional[float]
    month: str


class FeatureUsageResponse(BaseModel):
    success: bool
    data: Optional[FeatureUsageData] = None
    error: Optional[str] = None


@router.get("/{client_id}/", response_model=FeatureUsageResponse)
async def get_feature_usage(
    client_id: str,
    authorization: Optional[str] = Header(None),
) -> FeatureUsageResponse:
    """
    Retorna el uso real del mes actual:
    - posts_used: posts publicados/programados este mes
    - msgs_used: mensajes de NOVA consumidos este mes
    Incluye el límite del plan y el porcentaje de uso.
    """
    user = await get_current_user(authorization)
    supabase = get_supabase_service()

    if user.get("role") not in ("client", "owner", "reseller"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    client_row = supabase.client.table("clients").select("id, plan").eq("id", client_id).single().execute()
    if not client_row.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    plan = client_row.data.get("plan", "basic")
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).date().isoformat()
    month_label = now.strftime("%Y-%m")

    posts_rows = (
        supabase.client.table("scheduled_posts")
        .select("id", count="exact")
        .eq("client_id", client_id)
        .gte("scheduled_for", month_start)
        .execute()
    )
    posts_used = posts_rows.count or 0

    # Mensajes NOVA — tabla nova_messages si existe, si no retorna 0
    msgs_used = 0
    try:
        msgs_rows = (
            supabase.client.table("nova_messages")
            .select("id", count="exact")
            .eq("client_id", client_id)
            .gte("created_at", f"{month_start}T00:00:00+00:00")
            .execute()
        )
        msgs_used = msgs_rows.count or 0
    except Exception:
        msgs_used = 0

    limits = PLAN_LIMITS.get(plan, {"posts": 50, "msgs": 250})
    posts_limit = limits["posts"]
    msgs_limit = limits["msgs"]

    posts_pct = round((posts_used / posts_limit) * 100, 1) if posts_limit else None
    msgs_pct = round((msgs_used / msgs_limit) * 100, 1) if msgs_limit else None

    return FeatureUsageResponse(
        success=True,
        data=FeatureUsageData(
            client_id=client_id,
            plan=plan,
            posts_used=posts_used,
            posts_limit=posts_limit,
            posts_pct=posts_pct,
            msgs_used=msgs_used,
            msgs_limit=msgs_limit,
            msgs_pct=msgs_pct,
            month=month_label,
        ),
    )
