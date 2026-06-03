"""
Sentinel Router - Security & Monitoring
Filosofía: No velocity, only precision 🐢💎
"""
from fastapi import APIRouter, Query, Header, Request
from typing import Optional

from .handlers import (
    handle_get_status,
    handle_run_scan,
    handle_get_history,
    handle_deploy_check,
    ScanRequest,
    handle_ignore_issue,
    IssueActionRequest,
    handle_dispatch_fix,
    DispatchFixRequest,
    handle_security_scan_report,
    handle_get_latest_dependency_scan,
    SecurityScanReport,
    handle_secrets_rotation_status,
    handle_register_rotation,
    RegisterRotationRequest,
    handle_rls_audit_status,
    handle_rls_audit_trigger,
    handle_ai_providers_status,
    handle_frontend_error,
    FrontendError,
    handle_runtime_status,
)

router = APIRouter(prefix="/sentinel", tags=["SENTINEL 🛡️"])


@router.get("/status/")
async def get_status(authorization: Optional[str] = Header(None)):
    """Get current security status · solo owner/superadmin (4B-5)."""
    return await handle_get_status(authorization)


@router.post("/scan/")
async def run_scan(request: ScanRequest, authorization: Optional[str] = Header(None)):
    """Execute security scan (vault | pulse | db | full) · solo superadmin (4B-5)."""
    return await handle_run_scan(request, authorization)


@router.get("/history/")
async def get_history(
    limit: int = Query(default=30, description="Number of records"),
    agent_code: Optional[str] = Query(None, description="Filter by agent"),
    authorization: Optional[str] = Header(None),
):
    """Get scan history · solo superadmin (4B-5)."""
    return await handle_get_history(authorization, limit, agent_code)


@router.get("/deploy-check/")
async def deploy_check(authorization: Optional[str] = Header(None)):
    """Check if it's safe to deploy now · solo superadmin (4B-5)."""
    return await handle_deploy_check(authorization)


@router.post("/issues/ignore")
async def ignore_issue(request: IssueActionRequest, authorization: Optional[str] = Header(None)):
    """Marcar un issue como ignorado · solo superadmin."""
    return await handle_ignore_issue(request, authorization)


@router.post("/issues/dispatch-fix")
async def dispatch_fix(request: DispatchFixRequest, authorization: Optional[str] = Header(None)):
    """Despachar Fix de un issue (registra + devuelve prompt para Dev Chat) · solo superadmin."""
    return await handle_dispatch_fix(request, authorization)


@router.post("/security-scan-report")
async def security_scan_report(request: SecurityScanReport, x_sentinel_token: Optional[str] = Header(None)):
    """Receptor del GitHub Action (Capa 4) · auth X-Sentinel-Token (machine-to-machine)."""
    return await handle_security_scan_report(request, x_sentinel_token)


@router.get("/dependency-scans/latest")
async def dependency_scans_latest(authorization: Optional[str] = Header(None)):
    """Último dependency scan para el panel · solo superadmin."""
    return await handle_get_latest_dependency_scan(authorization)


@router.get("/secrets-rotation/status")
async def secrets_rotation_status(authorization: Optional[str] = Header(None)):
    """Estado de rotación de secrets (solo nombres · NUNCA valores) · solo superadmin."""
    return await handle_secrets_rotation_status(authorization)


@router.post("/secrets-rotation/register")
async def secrets_rotation_register(request: RegisterRotationRequest, authorization: Optional[str] = Header(None)):
    """Registrar rotación manual de un secret · solo superadmin."""
    return await handle_register_rotation(request, authorization)


@router.get("/rls-audit/latest")
async def rls_audit_latest(authorization: Optional[str] = Header(None)):
    """Última auditoría RLS · solo superadmin."""
    return await handle_rls_audit_status(authorization)


@router.post("/rls-audit/trigger")
async def rls_audit_trigger(authorization: Optional[str] = Header(None)):
    """Disparar auditoría RLS ahora ("Auditar ahora") · solo superadmin."""
    return await handle_rls_audit_trigger(authorization)


@router.get("/ai-providers/status")
async def ai_providers_status(authorization: Optional[str] = Header(None)):
    """Estado de AI providers (Anthropic/Bedrock/Vertex) + cobertura · solo superadmin."""
    return await handle_ai_providers_status(authorization)


@router.post("/runtime/frontend-error")
async def runtime_frontend_error(request: FrontendError, http_request: Request):
    """Receptor PÚBLICO de errores frontend (window.onerror/ErrorBoundary) · rate-limited por IP."""
    return await handle_frontend_error(request, http_request)


@router.get("/runtime/status")
async def runtime_status(authorization: Optional[str] = Header(None)):
    """Estado de observabilidad runtime (último scan + 24h) · solo superadmin."""
    return await handle_runtime_status(authorization)
