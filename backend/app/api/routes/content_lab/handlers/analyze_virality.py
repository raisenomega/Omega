"""
Handler de predicción de viralidad para Content Lab.
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging

from app.infrastructure.ai.claude_service import claude_service

logger = logging.getLogger(__name__)


async def handle_predict_virality(
    content: str,
    content_type: str,
    platform: str = "instagram"
) -> Dict[str, Any]:
    """
    Predice score de viralidad para contenido generado.

    Workflow:
    1. Analizar factores de viralidad (emociones, controversia, relevancia)
    2. Calcular score 0-1

    Args:
        content: Texto del contenido generado
        content_type: Tipo de contenido
        platform: Plataforma

    Returns:
        Dict con virality_score, factors, recommendations
    """
    try:
        # Construir prompt para predicción de viralidad
        prompt = (
            f"Analiza el potencial viral de este contenido de {platform}:\n\n"
            f"{content}\n\n"
            f"Evalúa (escala 0-10):\n"
            f"1. Impacto emocional\n"
            f"2. Relevancia/Tendencia actual\n"
            f"3. Llamado a compartir\n"
            f"4. Factor sorpresa/novedad\n"
            f"5. Controversia positiva\n\n"
            f"Da un score total y explica los factores clave."
        )

        # Generar análisis con Claude
        virality_analysis = await claude_service.generate_text(
            prompt=prompt,
            max_tokens=250,
            temperature=0.7
        )

        # Calcular score básico (fallback)
        # En producción, esto usaría un modelo ML entrenado
        base_score = 0.4  # Baseline

        # Factores que aumentan viralidad
        if len(content) < 150:  # Short & snappy
            base_score += 0.1
        if "?" in content:  # Questions engage
            base_score += 0.1
        if any(emoji in content for emoji in ["😍", "🔥", "💯", "✨"]):
            base_score += 0.1
        if content_type in ["reel", "video", "story"]:
            base_score += 0.2

        virality_score = min(base_score, 1.0)

        logger.info(
            f"Calculated virality score for {content_type}: {virality_score}"
        )

        return {
            "success": True,
            "virality_score": round(virality_score, 2),
            "virality_level": (
                "high" if virality_score >= 0.7 else
                "medium" if virality_score >= 0.4 else
                "low"
            ),
            "ai_analysis": virality_analysis,
            "key_factors": {
                "emotional_impact": round(virality_score * 0.9, 2),
                "shareability": round(virality_score * 0.85, 2),
                "trending_relevance": round(virality_score * 0.7, 2),
                "surprise_factor": round(virality_score * 0.6, 2)
            },
            "recommendations": [
                "Agregar más emociones fuertes" if virality_score < 0.5 else "Buen impacto emocional",
                "Incluir call-to-action para compartir" if "?" not in content else "Buen engagement",
                "Considerar formato video" if content_type not in ["reel", "video"] else "Formato óptimo"
            ]
        }

    except Exception as e:
        logger.error(f"Virality prediction failed: {e}")
        raise HTTPException(500, f"Error prediciendo viralidad: {str(e)}")
