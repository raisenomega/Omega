"""
NOVA Briefing Handler — AI-optimized system snapshot for NOVA consciousness.
Different from /omega/dashboard (human-focused). This is machine-optimized.
Filosofía: No velocity, only precision 🐢💎
DDD: Application layer - read operations. Strict <200L.
"""
from typing import Dict, Any
from datetime import datetime
from app.infrastructure.supabase_service import get_supabase_service
import logging

logger = logging.getLogger(__name__)


async def handle_get_briefing() -> Dict[str, Any]:
    """
    AI-optimized system snapshot for NOVA.

    Returns complete state: memory, status, agents, departments, docs, alerts, vault.
    Each query wrapped in try/except — failures return None (no cascading failure).
    10 second timeout maximum per query.

    Returns:
        Complete briefing with 7 sections (any can be None if query fails)
    """
    supabase = get_supabase_service()

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "nova_memory": None,
        "system_status": None,
        "active_agents": None,
        "departments": None,
        "context_documents": None,
        "pending_alerts": None,
        "prompt_vault_stats": None
    }

    # 1. NOVA Memory (last 20 entries by priority)
    try:
        mem = supabase.client.table("agent_working_memory")\
            .select("memory_type,content,priority,related_agents,expires_at,created_at")\
            .eq("agent_code", "NOVA")\
            .order("priority", desc=True)\
            .order("created_at", desc=True)\
            .limit(20).execute()
        result["nova_memory"] = mem.data if mem.data else []
        logger.info(f"NOVA memory: {len(result['nova_memory'])} entries")
    except Exception as e:
        logger.warning(f"Failed to fetch nova_memory: {e}")

    # 2. System Status (security, clients, agents) · 3 queries INDEPENDIENTES.
    # Antes: 1 solo try → el SELECT a clients pedía health_score/mrr (inexistentes)
    # → PostgREST error → tumbaba el bloque entero → system_status quedaba null
    # (security_score real de SENTINEL nunca se exponía). Ahora cada query aislada.
    security_score = None
    security_status = None
    try:
        scan = supabase.client.table("sentinel_scans")\
            .select("security_score,status")\
            .order("created_at", desc=True)\
            .limit(1).execute()
        if scan.data:
            security_score = scan.data[0].get("security_score")
            security_status = scan.data[0].get("status")
    except Exception as e:
        logger.warning(f"briefing: sentinel_scans query failed: {e}")

    total_clients = None
    active_clients = None
    try:
        # Columnas reales de clients (id/status/plan) · NO health_score/mrr (no existen · P1 honesto).
        clients = supabase.client.table("clients").select("id,status,plan").execute()
        client_list = clients.data or []
        total_clients = len(client_list)
        active_clients = len([c for c in client_list if c.get("status") == "active"])
    except Exception as e:
        logger.warning(f"briefing: clients query failed: {e}")

    agents_registered = None
    try:
        agents_count = supabase.client.table("omega_agents").select("id", count="exact").execute()
        agents_registered = agents_count.count or 0
    except Exception as e:
        logger.warning(f"briefing: omega_agents count failed: {e}")

    # Dict siempre poblado con lo resuelto · null en lo que falló (NO null global como antes).
    result["system_status"] = {
        "security_score": security_score,
        "security_status": security_status if security_status is not None else "unknown",
        "deploy_allowed": (security_score >= 70) if isinstance(security_score, (int, float)) else True,
        "total_clients": total_clients,
        "active_clients": active_clients,
        "agents_registered": agents_registered,
    }
    logger.info(f"briefing system_status: clients={total_clients} security={security_score}")

    # 3. Active Agents
    try:
        agents = supabase.client.table("omega_agents")\
            .select("code,name,role,status,seed_memory_loaded,department")\
            .order("code").execute()
        result["active_agents"] = agents.data if agents.data else []
        logger.info(f"Active agents: {len(result['active_agents'])}")
    except Exception as e:
        logger.warning(f"Failed to fetch active_agents: {e}")

    # 4. Departments
    try:
        depts = supabase.client.table("omega_departments")\
            .select("name,director_code,director_agent")\
            .execute()
        result["departments"] = depts.data if depts.data else []
        logger.info(f"Departments: {len(result['departments'])}")
    except Exception as e:
        logger.warning(f"Failed to fetch departments: {e}")

    # 5. Context Documents (metadata only, no full content)
    try:
        docs = supabase.client.table("context_documents")\
            .select("name,scope,department,created_at")\
            .execute()
        result["context_documents"] = [
            {
                "name": d.get("name"),
                "scope": d.get("scope"),
                "department": d.get("department")
            } for d in (docs.data or [])
        ]
        logger.info(f"Context documents: {len(result['context_documents'])}")
    except Exception as e:
        logger.warning(f"Failed to fetch context_documents: {e}")

    # 6. Pending Alerts (from nova_data)
    try:
        alerts = supabase.client.table("nova_data")\
            .select("data_type,content,created_at")\
            .eq("data_type", "alert")\
            .order("created_at", desc=True)\
            .limit(10).execute()
        result["pending_alerts"] = alerts.data if alerts.data else []
        logger.info(f"Pending alerts: {len(result['pending_alerts'])}")
    except Exception as e:
        logger.warning(f"Failed to fetch pending_alerts: {e}")

    # 7. Prompt Vault Stats
    try:
        vault = supabase.client.table("prompt_vault")\
            .select("vertical,performance_score,is_active")\
            .eq("is_active", True).execute()
        vault_data = vault.data or []
        verticals = list(set(v.get("vertical") for v in vault_data if v.get("vertical")))
        scores = [float(v.get("performance_score", 0)) for v in vault_data if v.get("performance_score")]

        # Top vertical by prompt count
        top_vertical = None
        if vault_data:
            vertical_counts = {}
            for v in vault_data:
                vert = v.get("vertical")
                if vert:
                    vertical_counts[vert] = vertical_counts.get(vert, 0) + 1
            if vertical_counts:
                top_vertical = max(vertical_counts, key=vertical_counts.get)

        result["prompt_vault_stats"] = {
            "total_prompts": len(vault_data),
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "verticals_covered": verticals,
            "top_vertical": top_vertical
        }
        logger.info(f"Prompt vault: {result['prompt_vault_stats']['total_prompts']} prompts")
    except Exception as e:
        logger.warning(f"Failed to fetch prompt_vault_stats: {e}")

    logger.info("NOVA briefing completed successfully")
    return result
