"""
System Router - Dynamic system statistics
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Request
from .handlers.get_stats import handle_get_stats
from .handlers.cron_status import handle_cron_status
from app.api.routes.auth.auth_utils import get_current_user

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/outcome-evaluator/run-now")
async def outcome_evaluator_run_now(authorization: Optional[str] = Header(None)):
    """DIAGNÓSTICO TEMPORAL (solo superadmin) · triggea run_outcome_evaluation() sin esperar
    el cron de las 4 AM. Retorna {evaluated, failed, errors}. Remover tras validar en prod."""
    user = await get_current_user(authorization)
    if user.get("role") != "owner":  # owner = superadmin real (00022)
        raise HTTPException(status_code=403, detail="superadmin_only")
    from app.bc_cognition.application.outcome_evaluator import run_outcome_evaluation
    return await run_outcome_evaluation()


@router.get("/credits/reset-now")
async def credit_period_reset_run_now(authorization: Optional[str] = Header(None)):
    """DIAGNÓSTICO TEMPORAL (solo superadmin · DEBT-052 F4) · triggea run_credit_period_reset()
    sin esperar el cron diario de 00:05. Retorna {reset, failed}. Remover tras validar en prod."""
    user = await get_current_user(authorization)
    if user.get("role") != "owner":  # owner = superadmin real (00022)
        raise HTTPException(status_code=403, detail="superadmin_only")
    from app.bc_billing.application.reset_credit_periods import run_credit_period_reset
    return await run_credit_period_reset()


@router.get("/cron-status")
async def cron_status(authorization: Optional[str] = Header(None)):
    """Estado de los cron jobs vs cron_registry (fuente única · P1-5) · solo superadmin.
    {expected, active, healthy, missing, unexpected, jobs}."""
    user = await get_current_user(authorization)
    if user.get("role") != "owner":  # owner = superadmin real (00022)
        raise HTTPException(status_code=403, detail="superadmin_only")
    return handle_cron_status()


@router.get("/stats")
async def get_system_stats(request: Request):
    """
    Get dynamic system statistics

    Returns real-time counts of:
    - total_endpoints: FastAPI routes count
    - total_agents / active_agents: agents with is_active=True
    - total_clients: clients (all · borrado es hard-delete)
    - total_scheduled_posts: scheduled posts activos (status='pending')
    - content_generated_today: content created today

    Cada count está aislado (degradación parcial · una query rota → 0, no 500).
    """
    return await handle_get_stats(request.app)
