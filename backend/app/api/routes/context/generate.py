"""
Context Brief Generation Endpoint
Generates AI-powered client brief from context profile
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from app.api.routes.context.models import (
    ClientContextResponse,
    ClientContextData
)
from app.api.routes.auth.jwt_utils import get_current_user_id
from app.infrastructure.repositories.context_repository import context_repository
from app.infrastructure.ai.claude_service import claude_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/{client_id}/generate-brief", response_model=ClientContextResponse)
async def generate_client_brief(
    client_id: str,
    authorization: Optional[str] = Header(None)
) -> ClientContextResponse:
    """
    Generate AI-powered client brief from context profile.

    Args:
        client_id: Client UUID
        authorization: JWT bearer token

    Returns:
        ClientContextResponse with updated context including ai_generated_brief

    Raises:
        HTTPException 401: Missing or invalid token
        HTTPException 403: Client trying to generate brief for another client
        HTTPException 404: Context not found for this client
        HTTPException 500: AI generation or database error

    Security:
        Verifies authenticated client_id matches requested client_id

    Notes:
        - Uses Claude to generate professional 200-300 word brief in Spanish
        - Brief includes all context fields: business, tone, goals, restrictions
        - Automatically updates context.ai_generated_brief in database
        - Temperature 0.5 for consistency, max_tokens 600 (~300 words)
    """
    try:
        # 1. Verify ownership
        authenticated_client_id = await get_current_user_id(authorization)
        if authenticated_client_id != client_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot generate brief for another client"
            )

        # 2. Get full context (404 if not exists)
        context = await context_repository.get_client_context(client_id)
        if not context:
            raise HTTPException(
                status_code=404,
                detail="Context not found for this client. Create context first."
            )

        # 3. Build prompt with all context fields
        system_message = (
            "You are a professional marketing strategist specializing in "
            "creating concise client briefs for AI content generation in "
            "Spanish. Generate briefs that capture the essence of a "
            "client's brand, audience, goals and restrictions in "
            "200-300 words. Always respond in Spanish."
        )

        prompt = f"""
Genera un brief profesional de cliente para generación de contenido basado en:

**Negocio:** {context.get('business_name', 'N/A')}
**Industria:** {context.get('industry', 'N/A')}
**Descripción:** {context.get('business_description', 'No especificada')}
**Tono de comunicación:** {context.get('communication_tone', 'N/A')}
**Objetivo principal:** {context.get('primary_goal', 'N/A')}
**Plataformas:** {', '.join(context.get('platforms', [])) or 'No especificadas'}
**Audiencia objetivo:** {context.get('target_audience', {}) or 'No especificada'}

**Palabras clave (USAR estas palabras):** {', '.join(context.get('keywords', [])) or 'Ninguna'}
**Palabras prohibidas (NUNCA usar):** {', '.join(context.get('forbidden_words', [])) or 'Ninguna'}
**Temas prohibidos (NUNCA mencionar):** {', '.join(context.get('forbidden_topics', [])) or 'Ninguno'}

**Instrucciones personalizadas:** {context.get('custom_instructions', 'Ninguna')}

Crea un brief conciso (200-300 palabras) que los generadores de contenido AI puedan usar como contexto. El brief debe ser claro, específico y capturar la esencia de la marca.
"""

        # 4. Call Claude to generate brief
        logger.info(f"Generating brief for client {client_id} using Claude")
        brief = await claude_service.generate_text(
            prompt=prompt,
            system_message=system_message,
            temperature=0.5,  # Consistent, not creative
            max_tokens=600    # ~300 words in Spanish
        )

        # 5. Update context with generated brief
        update_data = {"ai_generated_brief": brief}
        updated_context = await context_repository.update_client_context(
            client_id,
            update_data
        )

        logger.info(f"Brief generated and saved for client {client_id}")
        return ClientContextResponse(
            success=True,
            data=ClientContextData(**updated_context),
            message="Client brief generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating client brief: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating brief"
        )
