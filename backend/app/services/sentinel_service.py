"""
Sentinel Service - Security & Health Monitoring
Sistema inmune de OMEGA Company
Filosofía: No velocity, only precision 🐢💎
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from app.infrastructure.supabase_service import get_supabase_service
from app.services.sentinel_vault import run_vault_scan
from app.services.sentinel_pulse import run_pulse_monitor
from app.services.sentinel_db import run_db_guardian

logger = logging.getLogger(__name__)


class SentinelService:
    """Orquestador de los agentes VAULT, PULSE_MONITOR y DB_GUARDIAN."""

    def __init__(self):
        self.base_url = "https://omegaraisen-production-2031.up.railway.app/api/v1"

    def _prepare_for_insert(self, result: dict) -> dict:
        valid_cols = [
            "agent_code", "scan_type", "status", "security_score",
            "issues", "deploy_decision", "triggered_by", "scan_duration_ms",
        ]
        filtered = {k: v for k, v in result.items() if k in valid_cols}
        filtered.setdefault("auto_fixed", [])
        return filtered

    async def run_vault_scan(self) -> Dict[str, Any]:
        return await run_vault_scan()

    async def run_pulse_monitor(self) -> Dict[str, Any]:
        return await run_pulse_monitor()

    async def run_db_guardian(self) -> Dict[str, Any]:
        return await run_db_guardian()

    async def run_full_scan(self) -> Dict[str, Any]:
        """Ejecuta los 3 agentes en paralelo y calcula score global."""
        try:
            results = await asyncio.gather(
                self.run_vault_scan(),
                self.run_pulse_monitor(),
                self.run_db_guardian(),
                return_exceptions=True,
            )
            weights = {"VAULT": 0.35, "PULSE_MONITOR": 0.35, "DB_GUARDIAN": 0.30}
            global_score, all_issues = 0, []
            supabase = get_supabase_service()

            for result in results:
                if isinstance(result, dict):
                    agent = result["agent_code"]
                    global_score += result["security_score"] * weights.get(agent, 0.33)
                    all_issues.extend(result.get("issues", []))
                    insert_data = self._prepare_for_insert({**result, "triggered_by": "cron"})
                    supabase.client.table("sentinel_scans").insert(insert_data).execute()

            global_score = round(global_score)
            status = "presidencial" if global_score >= 85 else "warning" if global_score >= 70 else "critical"
            verdict = "DEPLOY" if global_score >= 75 else "DEPLOY_WITH_CAUTION" if global_score >= 60 else "DO_NOT_DEPLOY"
            supabase.client.table("sentinel_risk_scores").insert({
                "score": float(global_score),
                "security_score": float(global_score),
                "verdict": verdict,
                "issues_critical": len([i for i in all_issues if i["severity"] == "CRITICAL"]),
                "issues_high": len([i for i in all_issues if i["severity"] == "HIGH"]),
                "issues_medium": len([i for i in all_issues if i["severity"] == "MEDIUM"]),
                "issues_low": len([i for i in all_issues if i["severity"] == "LOW"]),
                "auto_fixes_applied": 0,
                "calculated_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            return {
                "security_score": global_score,
                "status": status,
                "deploy_decision": "BLOCK" if global_score < 70 else "APPROVE",
                "total_issues": len(all_issues),
                "critical_issues": len([i for i in all_issues if i["severity"] == "CRITICAL"]),
                "agents_scanned": len(results),
                "issues": all_issues,
            }
        except Exception as e:
            logger.error(f"Full scan error: {e}")
            return {"security_score": 0, "status": "critical", "deploy_decision": "BLOCK", "error": str(e)}
