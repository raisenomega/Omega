# backend/app/workers/competitor_tracker_worker.py
# MAX 200 LINES — R-LINES-001
# CompetitorTrackerWorker — Monitorea competidores por cliente

from __future__ import annotations
import asyncio
import logging
import time
from app.workers.base_worker import BaseWorker
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class CompetitorTrackerWorker(BaseWorker):
    """Monitorea competidores declarados en nova_context del cliente."""

    name = "competitor_tracker"

    async def execute(self, client_id: str) -> dict:
        """Ejecuta el tracker para un cliente específico"""
        supabase = get_supabase_service()
        competitors = await self._get_competitors(supabase, client_id)

        if not competitors:
            logger.info(f"[{self.name}] client={client_id} sin competidores declarados")
            return {"scanned": 0, "findings": 0}

        region = await self._get_client_region(supabase, client_id)
        total_findings = 0

        for competitor in competitors[:5]:
            findings = await self._scan_competitor(supabase, client_id, competitor, region)
            total_findings += findings
            await asyncio.sleep(1)

        logger.info(f"[{self.name}] client={client_id} competitors={len(competitors)} findings={total_findings}")
        return {"scanned": len(competitors[:5]), "findings": total_findings}

    async def _get_competitors(self, supabase, client_id: str) -> list[str]:
        """Lee competidores desde nova_context del cliente"""
        try:
            result = supabase.client.table("nova_context").select("competitors").eq("client_id", client_id).limit(1).execute()
            if not result.data:
                return []
            raw = result.data[0].get("competitors", "")
            if not raw:
                return []
            if isinstance(raw, list):
                return [c.strip() for c in raw if c.strip()]
            return [c.strip() for c in raw.split(",") if c.strip()]
        except Exception as e:
            logger.warning(f"[{self.name}] Error leyendo competidores: {e}")
            return []

    async def _get_client_region(self, supabase, client_id: str) -> str:
        """Lee región del cliente para contextualizar búsquedas"""
        try:
            result = supabase.client.table("nova_context").select("business_geo").eq("client_id", client_id).limit(1).execute()
            return result.data[0].get("business_geo", "Puerto Rico") if result.data else "Puerto Rico"
        except Exception:
            return "Puerto Rico"

    async def _scan_competitor(self, supabase, client_id: str, competitor: str, region: str) -> int:
        """Ejecuta 2 queries de búsqueda web (Brave) para un competidor y guarda resultados"""
        from app.infrastructure.tools.web_search_tool import web_search

        findings = []
        queries = [
            f"{competitor} noticias {region} 2026",
            f"{competitor} marketing campaña estrategia"
        ]

        for query in queries:
            try:
                result = await web_search(
                    query=query,
                    agent_code="COMPETITOR_TRACKER",
                    client_id=client_id,
                    max_results=3
                )
                if result.get("success") and result.get("results"):
                    relevant = self._filter_relevant(result["results"], competitor)
                    findings.extend(relevant)
            except Exception as e:
                logger.warning(f"[{self.name}] web_search error '{query}': {e}")

        if not findings:
            return 0

        await self._save_scan_activity(supabase, client_id, competitor, findings)
        critical = [f for f in findings if self._is_critical(f)]

        if critical:
            await self._create_approval_request(supabase, client_id, competitor, critical)

        return len(findings)

    def _filter_relevant(self, results: list, competitor: str) -> list:
        """Filtra resultados que mencionan al competidor"""
        competitor_lower = competitor.lower()
        return [
            r for r in results
            if competitor_lower in r.get("title", "").lower() or competitor_lower in r.get("content", "").lower()
        ]

    def _is_critical(self, finding: dict) -> bool:
        """Detecta hallazgos críticos: producto nuevo, precio, campaña viral"""
        critical_keywords = [
            "lanzamiento", "nuevo producto", "rebaja", "descuento",
            "viral", "campaña", "promoción", "oferta", "precio",
            "launch", "new product", "sale", "campaign"
        ]
        text = (finding.get("title", "") + " " + finding.get("content", "")).lower()
        return any(kw in text for kw in critical_keywords)

    async def _save_scan_activity(self, supabase, client_id: str, competitor: str, findings: list) -> None:
        """Guarda el scan en omega_activity"""
        try:
            activity_id = f"comp_scan_{client_id}_{int(time.time())}"
            supabase.client.table("omega_activity").insert({
                "id": activity_id,
                "client_id": client_id,
                "agent_code": "COMPETITOR_TRACKER",
                "type": "competitor_scan",
                "content": f"Scan completado: {competitor} — {len(findings)} hallazgos",
                "metadata": {
                    "competitor": competitor,
                    "findings_count": len(findings),
                    "findings": findings[:3]
                }
            }).execute()
        except Exception as e:
            logger.error(f"[{self.name}] Error guardando actividad: {e}")

    async def _create_approval_request(self, supabase, client_id: str, competitor: str, critical_findings: list) -> None:
        """Crea approval request para hallazgos críticos"""
        try:
            request_id = f"comp_alert_{client_id}_{int(time.time())}"
            titles = [f.get("title", "")[:80] for f in critical_findings[:3]]
            supabase.client.table("omega_approval_requests").insert({
                "id": request_id,
                "client_id": client_id,
                "agent_code": "COMPETITOR_TRACKER",
                "action_type": "competitor_alert",
                "payload": {
                    "competitor": competitor,
                    "critical_findings": titles
                },
                "context": {
                    "message": f"Actividad crítica detectada: {competitor}",
                    "urgency": "medium"
                },
                "status": "pending",
                "expires_at": None
            }).execute()
            logger.info(f"[{self.name}] Approval request creado para {competitor} | client={client_id}")
        except Exception as e:
            logger.error(f"[{self.name}] Error creando approval request: {e}")
