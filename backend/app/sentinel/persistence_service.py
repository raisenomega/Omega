# app/sentinel/persistence_service.py
"""
SENTINEL Persistence Service
Registra errores corregidos → genera reglas permanentes en Supabase.
Cada fix documentado aquí previene que el mismo error ocurra de nuevo.
MAX 200L — DDD compliant
"""
import logging
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from app.infrastructure.supabase_service import SupabaseService

logger = logging.getLogger(__name__)


@dataclass
class ErrorFix:
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


@dataclass
class RiskScoreData:
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


class PersistenceService:
    """
    Motor del bucle de mejora automática de SENTINEL.
    register_fix() → nueva regla permanente en Supabase.
    """

    def __init__(self, db: SupabaseService):
        self.db = db

    def register_fix(self, fix: ErrorFix) -> dict:
        """
        Registra un bug resuelto.
        Genera ID automático y guarda en omega_error_registry.
        """
        error_id = self._generate_error_id(fix.error_type)
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            self.db.client.table("omega_error_registry").insert({
                "error_id": error_id,
                "error_type": fix.error_type,
                "file_path": fix.file_path,
                "symptom": fix.symptom,
                "root_cause": fix.root_cause,
                "fix_description": fix.fix_description,
                "rule_code": fix.rule_code,
                "rule_text": fix.rule_text,
                "prevention": fix.prevention,
                "commit_hash": fix.commit_hash,
                "registered_by": fix.registered_by,
                "registered_at": timestamp,
            }).execute()
        except Exception as exc:
            logger.warning(
                "SENTINEL register_fix: no se pudo persistir %s en "
                "omega_error_registry (best-effort): %s",
                error_id, exc,
            )
            return {
                "success": False,
                "error_id": error_id,
                "rule_added": fix.rule_code,
                "message": f"Regla {fix.rule_code} no persistida: {exc}",
                "timestamp": timestamp,
            }

        return {
            "success": True,
            "error_id": error_id,
            "rule_added": fix.rule_code,
            "message": f"Regla {fix.rule_code} registrada permanentemente",
            "timestamp": timestamp,
        }

    def resolve_debt(self, debt_id: str, resolution: str) -> dict:
        """Marca una deuda técnica como resuelta."""
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            result = self.db.client.table("omega_tech_debt").update({
                "status": "resolved",
                "resolution": resolution,
                "resolved_at": timestamp,
            }).eq("debt_id", debt_id).execute()
        except Exception as exc:
            logger.warning(
                "SENTINEL resolve_debt: no se pudo actualizar %s en "
                "omega_tech_debt (best-effort): %s",
                debt_id, exc,
            )
            return {"success": False, "message": f"{debt_id} no persistida: {exc}"}

        if not result.data:
            return {"success": False, "message": f"{debt_id} no encontrada"}

        return {
            "success": True,
            "debt_id": debt_id,
            "resolution": resolution,
            "timestamp": timestamp,
        }

    def save_risk_score(self, data: RiskScoreData) -> dict:
        """Guarda el Risk Score calculado por SENT_BRAIN."""
        verdict = self._calculate_verdict(data.score)
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            self.db.client.table("sentinel_risk_scores").insert({
                "score": data.score,
                "security_score": data.security_score,
                "architecture_score": data.architecture_score,
                "performance_score": data.performance_score,
                "quality_score": data.quality_score,
                "deployment_score": data.deployment_score,
                "documentation_score": data.documentation_score,
                "verdict": verdict,
                "issues_critical": data.issues_critical,
                "issues_high": data.issues_high,
                "issues_medium": data.issues_medium,
                "issues_low": data.issues_low,
                "auto_fixes_applied": data.auto_fixes_applied,
                "calculated_at": timestamp,
            }).execute()
        except Exception as exc:
            logger.warning(
                "SENTINEL save_risk_score: no se pudo persistir score=%s en "
                "sentinel_risk_scores (best-effort): %s",
                data.score, exc,
            )
            return {
                "success": False,
                "score": data.score,
                "verdict": verdict,
                "timestamp": timestamp,
            }

        return {
            "success": True,
            "score": data.score,
            "verdict": verdict,
            "timestamp": timestamp,
        }

    def get_summary(self) -> dict:
        """
        Resumen del estado actual del sistema.
        Usado por NOVA para briefing diario.
        """
        try:
            errors = self.db.client.table("omega_error_registry")\
                .select("error_type", count="exact").execute()
            total_errors = errors.count or 0
        except Exception as exc:
            logger.warning(
                "SENTINEL get_summary: lectura de omega_error_registry "
                "falló (best-effort, default 0): %s", exc,
            )
            total_errors = 0

        try:
            debts = self.db.client.table("omega_tech_debt")\
                .select("debt_id, description, priority, status")\
                .eq("status", "active").execute()
            debts_data = debts.data or []
        except Exception as exc:
            logger.warning(
                "SENTINEL get_summary: lectura de omega_tech_debt "
                "falló (best-effort, default []): %s", exc,
            )
            debts_data = []

        try:
            latest_score = self.db.client.table("sentinel_risk_scores")\
                .select("score, verdict, calculated_at")\
                .order("calculated_at", desc=True)\
                .limit(1).execute()
            score_data = latest_score.data[0] if latest_score.data else None
        except Exception as exc:
            logger.warning(
                "SENTINEL get_summary: lectura de sentinel_risk_scores "
                "falló (best-effort, default None): %s", exc,
            )
            score_data = None

        return {
            "total_errors_registered": total_errors,
            "active_debts": len(debts_data),
            "debts": debts_data,
            "latest_risk_score": score_data,
        }

    # ── PRIVATE ──────────────────────────────────────────────

    def _generate_error_id(self, error_type: str) -> str:
        # microsegundos + sufijo aleatorio: evita colisión del UNIQUE (00029) en el mismo segundo
        from datetime import datetime, timezone
        from uuid import uuid4
        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        return f"ERR-{error_type}-{ts}-{uuid4().hex[:4]}"

    def _calculate_verdict(self, score: float) -> str:
        if score >= 75:
            return "DEPLOY"
        if score >= 60:
            return "DEPLOY_WITH_CAUTION"
        return "DO_NOT_DEPLOY"
