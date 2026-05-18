"""
ORACLE Intelligence Service
Genera briefs estratégicos semanales con análisis del sistema
Filosofía: No velocity, only precision 🐢💎
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class OracleService:
    """Servicio de inteligencia estratégica de ORACLE"""

    async def generate_intelligence_brief(self) -> Dict[str, Any]:
        """
        Genera OMEGA Intelligence Brief con datos reales del sistema
        Analiza: clientes, revenue, contenido, agentes, security
        """
        try:
            supabase = get_supabase_service()
            # 1. Métricas de clientes
            clients_resp = supabase.client.table("clients").select("*").execute()
            clients = clients_resp.data or []
            clients_active = [c for c in clients if c.get("status") == "active"]
            clients_by_plan = {}
            for c in clients:
                plan = c.get("plan", "unknown")
                clients_by_plan[plan] = clients_by_plan.get(plan, 0) + 1
            # 2. Contenido generado esta semana (disabled - table not available yet)
            content = []
            content_by_type = {}
            logger.info("Content generation stats not yet available")
            # 3. Resellers activos
            resellers_resp = supabase.client.table("resellers")\
                .select("id, agency_name, status")\
                .eq("status", "active")\
                .execute()
            resellers = resellers_resp.data or []
            # 4. Security score de SENTINEL
            last_scan_resp = supabase.client.table("sentinel_scans")\
                .select("security_score, status, created_at")\
                .order("created_at.desc")\
                .limit(1)\
                .execute()
            sentinel_score = None
            if last_scan_resp.data:
                sentinel_score = last_scan_resp.data[0].get("security_score")
            # 5. Construir brief
            brief = {
                "generated_at": datetime.utcnow().isoformat(),
                "period": "weekly",
                "week_of": datetime.utcnow().strftime("%Y-%m-%d"),
                "executive_summary": {
                    "total_clients": len(clients),
                    "active_clients": len(clients_active),
                    "clients_by_plan": clients_by_plan,
                    "total_resellers": len(resellers),
                    "sentinel_score": sentinel_score,
                },
                "content_intelligence": {
                    "total_generated_week": len(content),
                    "by_type": content_by_type,
                    "trend": "up" if len(content) > 10 else "stable" if len(content) > 0 else "no_activity"
                },
                "opportunities": self._detect_opportunities(clients, resellers),
                "alerts": self._detect_alerts(clients, sentinel_score),
                "recommendation": self._generate_recommendation(
                    len(clients_active), len(resellers), sentinel_score
                )
            }
            # 6. Guardar en nova_data para NOVA
            supabase.client.table("nova_data").upsert({
                "user_id": "ibrain",
                "data_type": "oracle_brief",
                "content": brief,
                "updated_at": datetime.utcnow().isoformat()
            }, on_conflict="user_id,data_type").execute()
            # 7. Guardar en omega_agent_memory para ORACLE
            supabase.client.table("omega_agent_memory").insert({
                "agent_code": "ORACLE",
                "memory_type": "brief_generated",
                "content": {
                    "timestamp": brief["generated_at"],
                    "week_of": brief["week_of"],
                    "clients_active": len(clients_active),
                    "content_generated": len(content),
                    "sentinel_score": sentinel_score
                },
                "session_id": f"oracle_{datetime.utcnow().strftime('%Y%m%d')}"
            }).execute()
            logger.info(f"ORACLE brief generated: {len(clients_active)} active clients, sentinel={sentinel_score}")
            return brief
        except Exception as e:
            logger.error(f"Error generating ORACLE brief: {e}")
            raise

    def _detect_opportunities(self, clients: List[Dict], resellers: List[Dict]) -> List[Dict]:
        """Detecta oportunidades estratégicas del negocio"""
        opportunities = []
        basic_clients = [c for c in clients if c.get("plan") == "basic"]
        if len(basic_clients) >= 3:
            opportunities.append({
                "type": "upsell",
                "priority": "HIGH",
                "description": f"{len(basic_clients)} clientes en Basic — candidatos para upgrade a Pro",
                "action": "SARA debe contactar para demo de features Pro"
            })
        if len(resellers) == 0:
            opportunities.append({
                "type": "reseller_expansion",
                "priority": "HIGH",
                "description": "Sin resellers activos — canal de expansión sin explotar",
                "action": "ATLAS debe activar campaña de reclutamiento reseller"
            })
        if len(clients) < 10:
            opportunities.append({
                "type": "growth",
                "priority": "MEDIUM",
                "description": f"Base de {len(clients)} clientes — oportunidad de crecimiento acelerado",
                "action": "LUAN debe escalar paid traffic en PR"
            })
        return opportunities

    def _detect_alerts(self, clients: List[Dict], sentinel_score: float | None) -> List[Dict]:
        """Detecta alertas críticas del sistema"""
        alerts = []
        if sentinel_score is not None and sentinel_score < 85:
            alerts.append({
                "type": "security",
                "severity": "HIGH",
                "description": f"SENTINEL score {sentinel_score} — debajo del threshold presidencial",
                "action": "Revisar issues en /omega/department/security"
            })
        inactive = [c for c in clients if c.get("status") != "active"]
        if len(inactive) > 0:
            alerts.append({
                "type": "churn_risk",
                "severity": "MEDIUM",
                "description": f"{len(inactive)} clientes inactivos",
                "action": "ANCHOR debe activar secuencia de retención"
            })
        return alerts

    def _generate_recommendation(self, active_clients: int, resellers: int, sentinel_score: float | None) -> str:
        """Genera recomendación estratégica basada en estado actual"""
        if sentinel_score and sentinel_score < 70:
            return "🔴 PRIORIDAD: Resolver issues de seguridad antes de cualquier acción comercial."
        if active_clients < 10:
            return "🎯 FOCO: Conseguir primeros 10 clientes activos pagando. Este es el trigger de Fase 1."
        if resellers == 0:
            return "🚀 OPORTUNIDAD: Infraestructura lista para primer reseller. ATLAS debe activar campaña."
        return "✅ Sistema estable. Escalar adquisición y activar ORACLE Intelligence ciclo semanal."
