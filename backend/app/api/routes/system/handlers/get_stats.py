"""
Handler: Get System Stats
Dynamic system statistics - no hardcoding
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Callable, Dict, Any, Optional
from fastapi import HTTPException, FastAPI
import logging
from datetime import date

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


def count_routes(app: FastAPI) -> int:
    """Count total registered routes in FastAPI app"""
    return len([r for r in app.routes if hasattr(r, 'methods')])


def _safe_count(label: str, build: Callable[[], Any]) -> int:
    """Count aislado · si la query falla (tabla/columna inexistente, etc.) loguea y
    devuelve 0. Una query rota NO tumba el endpoint completo (degradación parcial ·
    reemplaza el try monolítico previo)."""
    try:
        return build().count or 0
    except Exception as e:
        logger.warning(f"get_stats.{label} count failed: {e}")
        return 0


def count_active_agents() -> Optional[int]:
    """Conteo de agents activos para el /health. **None** si la query/init falla — el health debe
    poder reportar el FALLO en vez de inventar un número (cero-sintético P1). OJO: NO reusa
    _safe_count porque ese devuelve 0 on failure (conflación fallo-vs-0-real · la mentira que el
    /health justamente arrastraba con `count else 37`). Acá None=desconocido, 0=cero real."""
    try:
        sb = get_supabase_service().client
        return sb.table("agents").select("id", count="exact").eq("is_active", True).execute().count
    except Exception as e:
        logger.warning(f"count_active_agents failed: {e}")
        return None


def build_health(active: Optional[int], sha: str, environment: str) -> Dict[str, Any]:
    """Payload HONESTO del /health · status DERIVADO del conteo real. 'healthy' SOLO con conteo
    positivo; None (falló) o 0 (sin agentes) → 'degraded' con detail (jamás inventa un 37, jamás
    finge la fracción N/N). git_sha/environment se conservan (ya eran honestos)."""
    base = {"version": "2.0.0", "environment": environment, "git_sha": sha}
    if not active:
        return {**base, "status": "degraded",
                "detail": "agents_count_unavailable" if active is None else "no_active_agents"}
    return {**base, "status": "healthy", "agents_active": active}


async def handle_get_stats(app: FastAPI) -> Dict[str, Any]:
    """
    Estadísticas dinámicas del sistema. Cada count está aislado (try/except propio):
    si una query falla, ese campo cae a 0 y el resto responde igual.

    Returns dict:
        - total_endpoints: rutas FastAPI registradas
        - total_agents / active_agents: agentes con is_active=True
        - total_clients: clientes (todos · borrado es hard-delete, no soft via status)
        - total_scheduled_posts: posts programados activos (status='pending')
        - content_generated_today: contenido generado hoy

    Raises HTTPException 500 solo si falla la inicialización de Supabase.
    """
    try:
        sb = get_supabase_service().client
    except Exception as e:
        logger.error(f"get_stats · supabase init failed: {e}")
        raise HTTPException(status_code=500, detail="stats_unavailable")

    today = date.today().isoformat()
    total_endpoints = count_routes(app)
    total_agents = _safe_count("agents", lambda: sb.table("agents").select("id", count="exact").eq("is_active", True).execute())
    active_agents = _safe_count("active_agents", lambda: sb.table("agents").select("id", count="exact").eq("is_active", True).execute())
    total_clients = _safe_count("clients", lambda: sb.table("clients").select("id", count="exact").execute())
    total_scheduled_posts = _safe_count("scheduled_posts", lambda: sb.table("scheduled_posts").select("id", count="exact").eq("status", "pending").execute())
    content_generated_today = _safe_count("content_today", lambda: sb.table("content_lab_generated").select("id", count="exact").gte("created_at", f"{today}T00:00:00").lte("created_at", f"{today}T23:59:59").execute())

    logger.info(f"System stats: {total_endpoints} endpoints, {total_agents} agents, {total_clients} clients")
    return {
        "total_endpoints": total_endpoints,
        "total_agents": total_agents,
        "active_agents": active_agents,
        "total_clients": total_clients,
        "total_scheduled_posts": total_scheduled_posts,
        "content_generated_today": content_generated_today,
    }
