# backend/app/workers/trend_spotter_worker.py
# MAX 200 LINES — R-LINES-001
# TrendSpotterWorker — Detecta tendencias de industria por cliente

from __future__ import annotations
import asyncio
import logging
import time
from app.workers.base_worker import BaseWorker
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class TrendSpotterWorker(BaseWorker):
    """Detecta tendencias emergentes del nicho del cliente."""

    name = "trend_spotter"

    async def execute(self, client_id: str) -> dict:
        """Ejecuta el trend spotter para un cliente específico"""
        supabase = get_supabase_service()
        context = await self._get_client_context(supabase, client_id)
        niche = context.get("niche", "marketing digital")
        region = context.get("business_geo", "Puerto Rico")

        trends = await self._scan_trends(supabase, client_id, niche, region)

        logger.info(f"[{self.name}] client={client_id} niche={niche} trends={len(trends)}")
        return {"niche": niche, "trends_found": len(trends)}

    async def _get_client_context(self, supabase, client_id: str) -> dict:
        """Lee niche y región desde nova_context"""
        try:
            result = supabase.client.table("nova_context").select("niche, business_geo").eq("client_id", client_id).limit(1).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.warning(f"[{self.name}] Error leyendo contexto: {e}")
            return {}

    async def _scan_trends(self, supabase, client_id: str, niche: str, region: str) -> list:
        """Ejecuta 2 queries Tavily y retorna tendencias relevantes"""
        from app.infrastructure.tools.web_search_tool import web_search

        all_trends = []
        queries = [
            f"{niche} tendencias {region} 2026",
            f"marketing digital tendencias {region} 2026"
        ]

        for query in queries:
            try:
                result = await web_search(
                    query=query,
                    agent_code="TREND_SPOTTER",
                    client_id=client_id,
                    max_results=4
                )
                if result.get("success") and result.get("results"):
                    relevant = self._filter_trends(result["results"])
                    all_trends.extend(relevant)
            except Exception as e:
                logger.warning(f"[{self.name}] Tavily error '{query}': {e}")
            await asyncio.sleep(1)

        if not all_trends:
            return []

        await self._save_scan_activity(supabase, client_id, niche, all_trends)
        high_impact = [t for t in all_trends if self._is_high_impact(t)]

        if high_impact:
            await self._create_approval_request(supabase, client_id, niche, high_impact)

        return all_trends

    def _filter_trends(self, results: list) -> list:
        """Filtra resultados con señales de tendencia"""
        trend_keywords = [
            "tendencia", "trend", "viral", "crecimiento", "emergente",
            "nuevo", "auge", "popular", "rising", "growth", "2026"
        ]
        filtered = []
        for r in results:
            text = (r.get("title", "") + " " + r.get("content", "")).lower()
            if any(kw in text for kw in trend_keywords):
                filtered.append(r)
        return filtered

    def _is_high_impact(self, trend: dict) -> bool:
        """Detecta tendencias de alto impacto para alertar"""
        high_impact_keywords = [
            "viral", "explosivo", "boom", "record", "histórico",
            "masivo", "disruptivo", "revolutionary", "breakthrough"
        ]
        text = (trend.get("title", "") + " " + trend.get("content", "")).lower()
        return any(kw in text for kw in high_impact_keywords)

    async def _save_scan_activity(self, supabase, client_id: str, niche: str, trends: list) -> None:
        """Guarda el scan en omega_activity"""
        try:
            activity_id = f"trend_scan_{client_id}_{int(time.time())}"
            supabase.client.table("omega_activity").insert({
                "id": activity_id,
                "client_id": client_id,
                "agent_code": "TREND_SPOTTER",
                "type": "trend_scan",
                "content": f"Scan completado: {niche} — {len(trends)} tendencias",
                "metadata": {
                    "niche": niche,
                    "trends_count": len(trends),
                    "trends": trends[:3]
                }
            }).execute()
        except Exception as e:
            logger.error(f"[{self.name}] Error guardando actividad: {e}")

    async def _create_approval_request(self, supabase, client_id: str, niche: str, high_impact: list) -> None:
        """Crea approval request para tendencias de alto impacto"""
        try:
            request_id = f"trend_alert_{client_id}_{int(time.time())}"
            titles = [t.get("title", "")[:80] for t in high_impact[:3]]
            supabase.client.table("omega_approval_requests").insert({
                "id": request_id,
                "client_id": client_id,
                "agent_code": "TREND_SPOTTER",
                "action_type": "trend_alert",
                "payload": {
                    "niche": niche,
                    "high_impact_trends": titles
                },
                "context": {
                    "message": f"Tendencias de alto impacto detectadas: {niche}",
                    "urgency": "low"
                },
                "status": "pending",
                "expires_at": None
            }).execute()
            logger.info(f"[{self.name}] Approval request creado niche={niche} | client={client_id}")
        except Exception as e:
            logger.error(f"[{self.name}] Error creando approval request: {e}")
