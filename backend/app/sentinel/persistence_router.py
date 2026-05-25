# app/sentinel/persistence_router.py
"""
SENTINEL Persistence Endpoints
3 endpoints que conectan el sistema de aprendizaje con Railway.
Agregar al router existente de SENTINEL o importar en main.py.
MAX 200L — DDD compliant
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.infrastructure.supabase_service import get_supabase_service
from app.api.routes.auth.auth_utils import require_superadmin
from app.sentinel.persistence_service import (
    PersistenceService,
    ErrorFix,
    RiskScoreData,
)

router = APIRouter(prefix="/api/v1/sentinel", tags=["SENTINEL Persistence 🧠"])


# ── SCHEMAS ──────────────────────────────────────────────────

class RegisterFixRequest(BaseModel):
    error_type: str
    file_path: str
    symptom: str
    root_cause: str
    fix_description: str
    rule_code: str
    rule_text: str
    prevention: str
    commit_hash: Optional[str] = None
    registered_by: str = "IBRAIN"


class ResolveDebtRequest(BaseModel):
    resolution: str


class RiskScoreRequest(BaseModel):
    score: float
    security_score: Optional[float] = None
    architecture_score: Optional[float] = None
    performance_score: Optional[float] = None
    quality_score: Optional[float] = None
    deployment_score: Optional[float] = None
    documentation_score: Optional[float] = None
    issues_critical: int = 0
    issues_high: int = 0
    issues_medium: int = 0
    issues_low: int = 0
    auto_fixes_applied: int = 0


# ── ENDPOINTS ────────────────────────────────────────────────

@router.post("/register-fix")
async def register_fix(req: RegisterFixRequest, authorization: Optional[str] = Header(None)):
    """
    Registra un bug resuelto como regla permanente.
    Llamar después de cada fix + commit.

    Ejemplo:
    POST /api/v1/sentinel/register-fix
    {
      "error_type": "RUNTIME",
      "file_path": "app/calendar/domain/entities.py",
      "symptom": "422 en Calendar con account_id",
      "root_cause": "id: int en lugar de str",
      "fix_description": "Cambié id: int a id: str en ScheduledPost",
      "rule_code": "R-UUID-002",
      "rule_text": "Calendar entities también usan str para IDs",
      "prevention": "ARCH_SCAN detecta id: int en entities.py",
      "commit_hash": "abc123f"
    }
    """
    await require_superadmin(authorization)  # SENTINEL del sistema → solo superadmin (4B-5)
    try:
        valid_types = {
            "BUILD","RUNTIME","LOGIC","DB",
            "AUTH","PERF","DDD","TS","SEC","ARCH"
        }
        if req.error_type not in valid_types:
            raise HTTPException(
                status_code=422,
                detail=f"error_type debe ser uno de: {valid_types}"
            )

        db = get_supabase_service()
        service = PersistenceService(db)

        return service.register_fix(ErrorFix(
            error_type=req.error_type,
            file_path=req.file_path,
            symptom=req.symptom,
            root_cause=req.root_cause,
            fix_description=req.fix_description,
            rule_code=req.rule_code,
            rule_text=req.rule_text,
            prevention=req.prevention,
            commit_hash=req.commit_hash,
            registered_by=req.registered_by,
        ))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resolve-debt/{debt_id}")
async def resolve_debt(debt_id: str, req: ResolveDebtRequest, authorization: Optional[str] = Header(None)):
    """
    Marca una deuda técnica como resuelta.

    Ejemplo:
    POST /api/v1/sentinel/resolve-debt/DEBT-001
    { "resolution": "Dividido en reader.py + writer.py, ambos <200L" }
    """
    await require_superadmin(authorization)  # SENTINEL del sistema → solo superadmin (4B-5)
    db = get_supabase_service()
    service = PersistenceService(db)
    result = service.resolve_debt(debt_id, req.resolution)

    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.post("/risk-score")
async def save_risk_score(req: RiskScoreRequest, authorization: Optional[str] = Header(None)):
    """
    Guarda el Risk Score calculado por SENT_BRAIN.
    Se llama automáticamente desde el cron de las 7 AM.

    Score:
      90-100 → DEPLOY
      75-89  → DEPLOY (con nota)
      60-74  → DEPLOY_WITH_CAUTION
      0-59   → DO_NOT_DEPLOY
    """
    await require_superadmin(authorization)  # SENTINEL del sistema → solo superadmin (4B-5)
    if not 0 <= req.score <= 100:
        raise HTTPException(
            status_code=422,
            detail="score debe estar entre 0 y 100"
        )

    db = get_supabase_service()
    service = PersistenceService(db)

    return service.save_risk_score(RiskScoreData(
        score=req.score,
        security_score=req.security_score,
        architecture_score=req.architecture_score,
        performance_score=req.performance_score,
        quality_score=req.quality_score,
        deployment_score=req.deployment_score,
        documentation_score=req.documentation_score,
        issues_critical=req.issues_critical,
        issues_high=req.issues_high,
        issues_medium=req.issues_medium,
        issues_low=req.issues_low,
        auto_fixes_applied=req.auto_fixes_applied,
    ))


@router.get("/persistence-summary")
async def get_persistence_summary(authorization: Optional[str] = Header(None)):
    """
    Resumen del sistema de aprendizaje.
    NOVA lo usa para el briefing diario.

    Retorna:
    - Total errores registrados
    - Deudas técnicas activas
    - Último Risk Score
    """
    await require_superadmin(authorization)  # SENTINEL del sistema → solo superadmin (4B-5)
    db = get_supabase_service()
    service = PersistenceService(db)
    return service.get_summary()
