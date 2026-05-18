"""
Agent Memory Service
Gestiona memoria persistente de conversaciones para los 44 agentes organizacionales
Filosofía: No velocity, only precision 🐢💎
"""
from typing import List, Dict, Any
from datetime import datetime
import logging

from app.infrastructure.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)


class AgentMemoryService:
    """Servicio para gestionar memoria de agentes organizacionales"""

    # 44 agentes organizacionales de OMEGA Company
    AGENT_CODES = [
        'NOVA', 'ATLAS', 'LUNA', 'REX', 'VERA', 'KIRA', 'ORACLE', 'SOPHIA',
        'RAFA', 'DUDA', 'MAYA', 'LUAN', 'SARA', 'MALU', 'LOLA', 'DANI',
        'PIXEL', 'SHIELD', 'SCRIBE', 'PULSE_TECH', 'ARCH',
        'ONYX', 'ECHO', 'RESELL_OPS', 'ANCHOR', 'MIRROR_OPS',
        'LEDGER_FIN', 'GUARD', 'SCOPE', 'REPORT',
        'HAVEN', 'ESTATE', 'CONSTRUCT', 'NURTURE', 'REVIEW',
        'SCOUT', 'VEGA', 'NEXUS', 'MIRROR_FUT',
        'RECRUIT', 'TRAINER', 'PULSE', 'LEDGER_HR', 'PROMETHEUS'
    ]

    def extract_mentioned_agents(self, text: str) -> List[str]:
        """
        Detecta qué agentes se mencionan en el texto

        Args:
            text: Texto donde buscar menciones de agentes

        Returns:
            Lista de códigos de agentes mencionados
        """
        mentioned = []
        text_upper = text.upper()

        for code in self.AGENT_CODES:
            if code in text_upper:
                mentioned.append(code)

        return mentioned

    async def save_conversation_memory(
        self,
        agent_codes: List[str],
        user_message: str,
        nova_response: str,
        recent_context: List[Dict[str, Any]]
    ) -> None:
        """
        Guarda memoria de conversación para cada agente mencionado

        Args:
            agent_codes: Lista de códigos de agentes
            user_message: Mensaje del usuario
            nova_response: Respuesta de NOVA
            recent_context: Últimos mensajes de contexto
        """
        if not agent_codes:
            return

        try:
            supabase = get_supabase_service()
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M')}"

            for agent_code in agent_codes:
                memory_content = {
                    "user_message": user_message[:500],  # Limitar longitud
                    "nova_response": nova_response[:500],
                    "timestamp": datetime.utcnow().isoformat(),
                    "context": [
                        {
                            "role": msg.get("role"),
                            "content": msg.get("content", "")[:200]
                        }
                        for msg in recent_context[-3:]
                    ] if recent_context else [],
                    "session_id": session_id
                }

                try:
                    supabase.client.table("omega_agent_memory").insert({
                        "agent_code": agent_code,
                        "memory_type": "conversation",
                        "content": memory_content
                    }).execute()

                    logger.info(f"Memory saved for agent: {agent_code}")

                except Exception as e:
                    logger.warning(f"Failed to save memory for {agent_code}: {e}")

        except Exception as e:
            logger.error(f"Error in save_conversation_memory: {e}")

    async def get_agent_context(self, agent_code: str, limit: int = 5) -> str:
        """
        Recupera últimas memorias de un agente para contexto

        Args:
            agent_code: Código del agente
            limit: Número máximo de memorias a recuperar

        Returns:
            String con contexto formateado de memorias recientes
        """
        try:
            supabase = get_supabase_service()

            result = supabase.client.table("omega_agent_memory")\
                .select("*")\
                .eq("agent_code", agent_code.upper())\
                .order("updated_at", desc=True)\
                .limit(limit)\
                .execute()

            if not result.data:
                return ""

            context_parts = []
            for mem in result.data:
                content = mem.get("content", {})
                timestamp = content.get("timestamp", "")[:16]  # Solo fecha y hora
                user_msg = content.get("user_message", "")[:100]
                nova_resp = content.get("nova_response", "")[:100]

                if user_msg and nova_resp:
                    context_parts.append(
                        f"[{timestamp}] Ibrain: {user_msg}... | NOVA: {nova_resp}..."
                    )

            if context_parts:
                return "\n".join(context_parts)

            return ""

        except Exception as e:
            logger.error(f"Error getting agent context for {agent_code}: {e}")
            return ""
