# backend/app/workers/news_monitor_worker.py
# MAX 200 LINES — R-LINES-001
# News Monitor Worker — monitorea noticias de industria cada 2h
# Primer worker autónomo de OMEGA v2

from __future__ import annotations
import time
import logging
from app.workers.base_worker import BaseWorker
from app.infrastructure.tools.web_search_tool import web_search
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class NewsMonitorWorker(BaseWorker):
    """
    Busca noticias relevantes para la industria de cada cliente.
    Corre cada 2 horas via APScheduler.
    Genera alertas si detecta noticias críticas.
    """

    name = "news_monitor"

    async def execute(self, client_id: str) -> dict:
        """
        1. Obtiene contexto del cliente (industria, nombre de marca)
        2. Busca noticias relevantes via búsqueda web (Brave)
        3. Guarda resultados en omega_activity
        4. Crea approval_request si hay noticia crítica
        """
        # 1. Cargar contexto del cliente
        context = await self._load_client_context(client_id)
        if not context:
            return {"skipped": True, "reason": "no_client_context"}

        industry  = context.get("industry", "marketing digital")
        brand     = context.get("brand_name", "la marca")
        region    = context.get("region", "Puerto Rico")

        # 2. Buscar noticias — 2 búsquedas: industria + marca
        queries = [
            f"{industry} noticias tendencias {region} 2026",
            f"marketing digital {region} novedades esta semana",
        ]

        all_results = []
        for query in queries:
            result = await web_search(
                query      = query,
                agent_code = "NEWS_MONITOR",
                client_id  = client_id,
                max_results = 3,
            )
            if result.get("success"):
                all_results.extend(result.get("results", []))

        if not all_results:
            return {"news_found": 0, "status": "no_results"}

        # 3. Evaluar si alguna noticia es crítica
        critical = self._detect_critical(all_results, brand)

        # 4. Guardar en omega_activity
        await self._save_activity(
            client_id = client_id,
            results   = all_results,
            industry  = industry,
        )

        # 5. Si hay noticia crítica → approval request para que el cliente vea
        if critical:
            await self._create_alert(client_id, critical)

        return {
            "news_found":    len(all_results),
            "critical_alert": critical is not None,
            "queries_run":   len(queries),
            "industry":      industry,
        }

    async def _load_client_context(self, client_id: str) -> dict | None:
        """Obtiene industria y nombre de marca del cliente."""
        try:
            supabase = get_supabase_service()

            # Intentar desde clients tabla
            result = (
                supabase.client.table("clients")
                .select("business_name, industry, city, country")
                .eq("id", client_id)
                .limit(1)
                .execute()
            )
            if result.data:
                row = result.data[0]
                return {
                    "brand_name": row.get("business_name", ""),
                    "industry":   row.get("industry", "marketing digital"),
                    "region":     row.get("city") or row.get("country") or "Puerto Rico",
                }
        except Exception as e:
            logger.warning(f"[news_monitor] context error client={client_id}: {e}")
        return None

    def _detect_critical(
        self,
        results: list[dict],
        brand: str,
    ) -> dict | None:
        """
        Detecta si alguna noticia requiere atención inmediata.
        Criterio: mención directa de la marca o palabras de crisis.
        """
        crisis_keywords = [
            "crisis", "escándalo", "demanda", "multa", "cierre",
            "quiebra", "fraude", "viral negativo", "boicot",
        ]
        brand_lower = brand.lower()

        for item in results:
            content = (item.get("content", "") + item.get("title", "")).lower()
            if brand_lower and brand_lower in content:
                return {"type": "brand_mention", "item": item}
            if any(kw in content for kw in crisis_keywords):
                return {"type": "crisis_keyword", "item": item}
        return None

    async def _save_activity(
        self,
        client_id: str,
        results: list[dict],
        industry: str,
    ) -> None:
        """Guarda resumen de noticias en omega_activity."""
        try:
            supabase = get_supabase_service()
            summary  = "; ".join(
                r.get("title", "")[:80]
                for r in results[:3]
            )
            supabase.client.table("omega_activity").insert({
                "id":         f"news_{client_id}_{int(time.time())}",
                "client_id":  client_id,
                "agent_code": "NEWS_MONITOR",
                "type":       "news_scan",
                "content":    summary[:500],
                "metadata": {
                    "count":    len(results),
                    "industry": industry,
                    "sources":  [r.get("url", "") for r in results[:5]],
                },
            }).execute()
        except Exception as e:
            logger.warning(f"[news_monitor] activity save error: {e}")

    async def _create_alert(
        self,
        client_id: str,
        critical: dict,
    ) -> None:
        """Crea approval_request urgente para el cliente."""
        try:
            item = critical.get("item", {})
            supabase = get_supabase_service()
            supabase.client.table("omega_approval_requests").insert({
                "id":          f"news_alert_{client_id}_{int(time.time())}",
                "client_id":   client_id,
                "agent_code":  "NEWS_MONITOR",
                "action_type": "news_alert",
                "payload": {
                    "title":   item.get("title", ""),
                    "url":     item.get("url", ""),
                    "content": item.get("content", "")[:500],
                    "type":    critical.get("type"),
                },
                "context": {
                    "message": "OMEGA detectó una noticia que requiere tu atención.",
                    "urgency": "high",
                },
                "status":     "pending",
                "expires_at": None,
            }).execute()
            logger.info(f"[news_monitor] alert created for client={client_id}")
        except Exception as e:
            logger.warning(f"[news_monitor] alert creation error: {e}")
