"""Platform public routes — landing pública de OMEGA (marca OMEGA · sin auth).

POST /platform/lead: capta leads de plataforma (reseller_id NULL + audience). Espejo del
patrón resellers/public.py, pero SERVER-SIDE fuerza reseller_id=NULL y source, valida audience,
aplica honeypot + rate-limit dedicado por IP (más estricto que el global de 300/min).
"""
import time
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Header

from app.infrastructure.supabase_service import get_supabase_service
from app.models.shared_models import APIResponse
from app.models.platform_models import CreatePlatformLeadRequest
from app.api.routes.auth.super_owner import require_super_owner

router = APIRouter(prefix="/platform", tags=["platform"])
logger = logging.getLogger(__name__)

# Rate-limit dedicado: 5 envíos/hora/IP · in-memory fixed-window · single-instance (consistente
# con rate_limit_middleware · Railway 1 instancia; escalar horizontal requeriría store compartido).
_WINDOW_S = 3600.0
_MAX_PER_WINDOW = 5
_hits: dict[str, list[float]] = {}


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")  # Railway/proxy → IP real es la primera
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _rate_limited(ip: str) -> bool:
    now = time.monotonic()
    window_start = now - _WINDOW_S
    hits = [t for t in _hits.get(ip, ()) if t > window_start]
    if len(hits) >= _MAX_PER_WINDOW:
        _hits[ip] = hits
        return True
    hits.append(now)
    _hits[ip] = hits
    return False


@router.post("/lead", response_model=APIResponse)
async def create_platform_lead(request: Request, body: CreatePlatformLeadRequest) -> APIResponse:
    """Lead público de la landing de plataforma (reseller_id NULL · audience pyme|reseller)."""
    # Honeypot: bots llenan `website`, humanos no → success silencioso SIN insertar (no avisa al bot).
    if body.website.strip():
        return APIResponse(success=True, data={}, message="Lead received successfully")

    if _rate_limited(_client_ip(request)):
        raise HTTPException(status_code=429, detail="rate_limited")

    try:
        service = get_supabase_service()
        lead_data = {
            "reseller_id": None,            # SIEMPRE NULL (lead de plataforma · nunca del body)
            "audience": body.audience,      # pyme|reseller (Literal) · CHECK de leads = 2ª barrera
            "name": body.name,
            "email": str(body.email),
            "phone": body.phone,
            "message": body.message,
            "source": "omega_landing",      # forzado
            "consent_given": True,          # legítimo: el form muestra el aviso de consentimiento
            "consent_date": datetime.now(timezone.utc).isoformat(),
        }
        await service.create_lead(lead_data)
        return APIResponse(success=True, data={}, message="Lead received successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating platform lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leads", response_model=APIResponse)
async def list_platform_leads(
    audience: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    authorization: Optional[str] = Header(None),
) -> APIResponse:
    """Inbox de leads de plataforma (reseller_id NULL) · SOLO super_owner · lo consume /web/leads."""
    await require_super_owner(authorization)  # 401 sin token · 403 si no super_owner
    if limit > 100:
        limit = 100
    service = get_supabase_service()
    leads, total = await service.get_platform_leads(audience, status, page, limit)
    return APIResponse(
        success=True,
        data={"leads": leads, "total": total, "page": page, "limit": limit},
        message=f"Found {total} leads",
    )
