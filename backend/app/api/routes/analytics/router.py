"""
Analytics API Routes
Dashboard de analytics con datos REALES de Supabase (GET /dashboard/).

Los endpoints legacy de muestra (analyze-metrics / detect-patterns / generate-insights / forecast /
dashboard-data / agent-status) fueron ELIMINADOS: sin consumidor y con datos sintéticos hardcodeados
(12500 seguidores, 4.2% engagement, followers=1000 default) = violación P1 de la regla GLOBAL
cero-sintéticos. Las métricas reales de redes salen de /intelligence/analytics (Zernio · snapshot real).
"""
from fastapi import APIRouter, Header, Query
from pydantic import BaseModel
from typing import Optional
from app.api.routes.analytics.handlers.get_dashboard import handle_get_dashboard
from app.api.routes.auth.auth_utils import get_current_user, require_superadmin
from app.api.routes.calendar_v3._access import resolve_client_or_403

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsResponse(BaseModel):
    """Generic analytics response"""
    success: bool
    data: dict
    message: Optional[str] = None


@router.get("/dashboard/", response_model=AnalyticsResponse)
async def get_dashboard(
    client_id: Optional[str] = Query(None, description="Client UUID · None = aggregate-all (solo owner)"),
    date_range: str = Query(default="7d", description="Time range: 7d, 30d, 90d"),
    authorization: Optional[str] = Header(None),
) -> AnalyticsResponse:
    """
    Get analytics dashboard with real Supabase data

    - **client_id**: Optional client UUID (if None, aggregate all clients)
    - **date_range**: Time range (7d, 30d, 90d)

    Returns content_generated, scheduled_posts, client_context stats
    """
    # IDOR fix: None → aggregate-all gated a owner (require_superadmin) · con client_id → ownership
    # vía resolve_client_or_403 (variante A · calendar_v3._access · sin fallback · molde 5727dda).
    if client_id is None:
        await require_superadmin(authorization)
        validated_client_id: Optional[str] = None
    else:
        user = await get_current_user(authorization)
        client = resolve_client_or_403(user["id"], client_id)
        validated_client_id = str(client["id"])
    result = await handle_get_dashboard(client_id=validated_client_id, date_range=date_range)
    return AnalyticsResponse(
        success=True,
        data=result,
        message="Dashboard data retrieved successfully"
    )
