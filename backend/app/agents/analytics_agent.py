"""
Analytics Agent
Genera insights de IA (texto) sobre métricas de CONTENIDO · usado por Content Lab.

Las métricas REALES de redes (seguidores/engagement/posts) vienen del endpoint honesto
/intelligence/analytics (Zernio · snapshot real). Este agente NO genera dashboards ni números:
solo texto de insights sobre el contenido. Cero datos sintéticos (regla GLOBAL P1).
"""
from typing import Dict, Any
from datetime import datetime
import logging
from app.agents.base_agent import BaseAgent, AgentRole, AgentState
from app.infrastructure.ai.claude_service import claude_service
from app.bc_cognition.domain.routing_table import resolve_model

logger = logging.getLogger(__name__)


class AnalyticsAgent(BaseAgent):
    """Agente de insights de IA sobre métricas de contenido (Content Lab).

    Solo task type "insights" (texto). Sin generación de dashboards/forecast/patterns sintéticos:
    esos endpoints legacy fueron eliminados (datos de muestra = violación P1). Las métricas reales
    de redes salen de Zernio vía /intelligence/analytics.
    """

    def __init__(self, agent_id: str = "analytics_001"):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYTICS,
            model=resolve_model("analytics"),  # I2: sonnet
            tools=["insight_generator"],
        )

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta tarea de analytics · solo 'insights' (texto IA sobre métricas de contenido)."""
        self.set_state(AgentState.WORKING)
        try:
            if task.get("type") != "insights":
                raise ValueError(f"Unsupported task type: {task.get('type')}")
            result = await self._generate_insights(task)
            await self.store_memory("last_insights", result)
            self.set_state(AgentState.IDLE)
            return result
        except Exception as e:
            logger.error(f"Analytics execution error: {e}")
            self.set_state(AgentState.ERROR)
            raise

    async def _generate_insights(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Genera insights accionables sobre las métricas (texto IA · sin números sintéticos)."""
        metrics = task.get("metrics", {})
        prompt = self._build_insights_prompt(metrics)
        insights_text = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=400,
            temperature=0.7,
            model=self.model,
        )
        return {
            "insights": insights_text,
            "metrics_analyzed": list(metrics.keys()),
            "generated_at": datetime.now().isoformat(),
        }

    def _build_insights_prompt(self, metrics: Dict[str, Any]) -> str:
        """Construye el prompt de insights a partir de las métricas provistas."""
        prompt_parts = ["Generate actionable insights from these metrics:", ""]
        for key, value in metrics.items():
            prompt_parts.append(f"- {key}: {value}")
        prompt_parts.extend([
            "",
            "Provide:",
            "1. Key observations",
            "2. Areas of concern",
            "3. Opportunities for improvement",
            "4. Specific action items",
        ])
        return "\n".join(prompt_parts)


# Global instance
analytics_agent = AnalyticsAgent()
