"""SENTINEL Capa 6 — auditoría RLS horaria. Invoca public.sentinel_rls_audit() (SECURITY DEFINER)
y persiste la corrida en sentinel_rls_audits. Module-based (matchea decision_evaluator)."""
import logging
from typing import Dict, Any

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


async def run_rls_audit_scan() -> Dict[str, Any]:
    """Corre la auditoría RLS y guarda el resultado · loguea warning si hay críticas."""
    sb = get_supabase_service().client
    rpc = sb.rpc("sentinel_rls_audit").execute()
    result = rpc.data if isinstance(rpc.data, dict) else {}
    by_sev = result.get("by_severity", {}) if isinstance(result.get("by_severity"), dict) else {}
    row = {
        "scanned_at": result.get("scanned_at"),
        "total_tables": result.get("total_tables", 0),
        "total_issues": result.get("total_issues", 0),
        "severity_critical": by_sev.get("critical", 0),
        "severity_high": by_sev.get("high", 0),
        "severity_medium": by_sev.get("medium", 0),
        "issues": result.get("issues", []),
    }
    ins = sb.table("sentinel_rls_audits").insert(row).execute()
    audit_id = (ins.data or [{}])[0].get("id")
    if row["severity_critical"] > 0:
        logger.warning(f"SENTINEL RLS: {row['severity_critical']} CRÍTICAS · {row['total_issues']} issues totales")
    else:
        logger.info(f"SENTINEL RLS: {row['total_issues']} issues ({row['severity_high']} high)")
    return {"success": True, "audit_id": audit_id, "total_issues": row["total_issues"]}
