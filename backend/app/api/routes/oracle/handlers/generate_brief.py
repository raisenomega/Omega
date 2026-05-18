"""
Handler: Generate ORACLE Brief
POST /oracle/brief/generate/ - Genera nuevo intelligence brief
Filosofía: No velocity, only precision 🐢💎
"""
from typing import Dict, Any
from fastapi import HTTPException
import logging
from app.services.oracle_service import OracleService

logger = logging.getLogger(__name__)


async def handle_generate_brief() -> Dict[str, Any]:
    """
    Generate new ORACLE Intelligence Brief
    Fuerza la generación de un brief nuevo con datos actuales

    Returns:
        Dict with newly generated brief

    Raises:
        HTTPException 500: Generation error
    """
    try:
        logger.info("Manual ORACLE brief generation requested")

        oracle = OracleService()
        brief = await oracle.generate_intelligence_brief()

        return {
            "success": True,
            "brief": brief,
            "generated_at": brief.get("generated_at"),
            "message": "ORACLE Intelligence Brief generated successfully"
        }

    except Exception as e:
        logger.error(f"Error generating ORACLE brief: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate ORACLE brief: {str(e)}"
        )
