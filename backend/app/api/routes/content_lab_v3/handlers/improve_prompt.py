"""POST /api/v1/content-lab/improve-prompt · UX-2.

Llama Claude Haiku via anthropic_adapter (agent_code='caption_optimizer' · DDD I2)
para mejorar el brief crudo del usuario. Devuelve UNA versión mejorada: más
específica, accionable, con audiencia clara y angle concreto. Mantiene la
intención original · cero invenciones.

El frontend muestra panel con [Aceptar] [Rechazar] · el usuario decide.
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3.models.content_lab_models import (
    ImprovePromptRequest, ImprovePromptResponse,
)
from app.bc_cognition.infrastructure.anthropic_adapter import generate

router = APIRouter()

_SYSTEM = (
    "Sos un editor de briefs para contenido social. Recibís un brief crudo "
    "del usuario y devolvés UNA versión mejorada: más específica, accionable, "
    "con audiencia clara y angle concreto.\n\n"
    "Reglas:\n"
    "- Mantené la intención original · cero invenciones\n"
    "- Max 300 chars output\n"
    "- Sin meta-comentarios ni explicación · SOLO el brief mejorado\n"
    "- Tono natural en español rioplatense neutro"
)


@router.post("/improve-prompt", response_model=ImprovePromptResponse)
async def improve_prompt(
    request: ImprovePromptRequest,
    authorization: Optional[str] = Header(None),
) -> ImprovePromptResponse:
    await get_current_user(authorization)  # auth requerido · no necesita client_id
    user_content = (
        f"Plataforma: {request.platform or 'general'} · "
        f"Tipo: {request.content_type or 'caption'}\n\n"
        f"Brief original:\n{request.original_prompt}"
    )
    response, error = await generate(
        agent_code="caption_optimizer",  # I2 → Haiku 4.5
        system=_SYSTEM,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=200,
        temperature=0.7,
    )
    if error is not None or response is None:
        code = error.code if error else "unknown"
        raise HTTPException(status_code=503, detail=f"improve_failed:{code}")
    return ImprovePromptResponse(improved_prompt=response.text.strip())
