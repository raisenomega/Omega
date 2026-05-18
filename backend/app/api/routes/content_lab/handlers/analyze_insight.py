"""
Handler de análisis de insights para Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.agents.analytics_agent import analytics_agent
from app.infrastructure.ai.openai_service import openai_service

logger = logging.getLogger(__name__)


async def handle_analyze_insight(
    content: str,
    content_type: str,
    platform: str = "instagram"
) -> Dict[str, Any]:
    """
    Analiza contenido generado y proporciona insights.

    Workflow:
    1. Usar Analytics Agent para generar insights
    2. Proporcionar recomendaciones específicas

    Args:
        content: Texto del contenido generado
        content_type: Tipo de contenido (caption, story, etc.)
        platform: Plataforma (instagram, facebook, etc.)

    Returns:
        Dict con insights, recommendations, tone_analysis
    """
    try:
        # Construir prompt para análisis de contenido
        prompt = (
            f"Analiza este contenido de {platform} ({content_type}):\n\n"
            f"{content}\n\n"
            f"Proporciona:\n"
            f"1. ¿Qué funciona bien? (3 puntos)\n"
            f"2. ¿Qué se puede mejorar? (2 puntos)\n"
            f"3. Análisis de tono (profesional/casual/emocional/etc.)\n"
            f"4. Llamado a la acción: ¿es efectivo?"
        )

        # Generar análisis con OpenAI
        analysis_text = await openai_service.generate_text(
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )

        # Usar Analytics Agent para métricas adicionales
        metrics = {
            "content_length": len(content),
            "content_type": content_type,
            "platform": platform
        }

        agent_insights = await analytics_agent.execute({
            "type": "insights",
            "metrics": metrics
        })

        logger.info(
            f"Generated insights for {content_type} content "
            f"({len(content)} chars)"
        )

        return {
            "success": True,
            "insights": analysis_text,
            "ai_analysis": agent_insights.get("insights", ""),
            "content_metrics": {
                "length": len(content),
                "estimated_read_time_seconds": len(content.split()) * 0.5
            }
        }

    except Exception as e:
        logger.error(f"Insight analysis failed: {e}")
        raise HTTPException(500, f"Error generando insights: {str(e)}")
