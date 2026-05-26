"""POST /api/v1/content-lab/research · Brave Search wrapper.

Cablea el botón 'Research' del Content Lab form bar al BRAVE_API_KEY ya
configurada en Railway · consumida por web_search_tool legacy. Cero
acoplamiento a agentes legacy · handler dedicado para uso de usuario
final (no agente autónomo).

Errores HTTP semánticos:
- 400 query_too_short  (validación Pydantic min_length=3)
- 503 brave_not_configured / brave_unavailable / brave_timeout
- 500 unknown_research_error
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException

from app.api.routes.auth.auth_utils import get_current_user
from app.api.routes.content_lab_v3.models.content_lab_models import (
    ResearchRequest, ResearchResponse, ResearchResult,
)
from app.infrastructure.tools.web_search_tool import web_search
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction

router = APIRouter()

_UNSAFE = (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW)


def _safe_result(r: dict) -> Optional[ResearchResult]:
    """Sanitiza snippet externo (T2 · RESEARCH_SNIPPET). Inseguro → None (descartar)."""
    out, err = sanitize_input(str(r.get("content") or r.get("snippet") or ""), InputContext.RESEARCH_SNIPPET)
    if err is not None or out is None or out.action in _UNSAFE:
        return None
    return ResearchResult(title=str(r.get("title", "")), url=str(r.get("url", "")), snippet=out.clean_text)


def _safe_answer(answer: object) -> Optional[str]:
    """Sanitiza el answer externo de Brave (T2). Inseguro/vacío → None."""
    if not answer:
        return None
    out, err = sanitize_input(str(answer), InputContext.RESEARCH_SNIPPET)
    return None if (err is not None or out is None or out.action in _UNSAFE) else out.clean_text


@router.post("/research", response_model=ResearchResponse)
async def research(
    request: ResearchRequest,
    authorization: Optional[str] = Header(None),
) -> ResearchResponse:
    user = await get_current_user(authorization)
    result = await web_search(
        query=request.query,
        agent_code="content_creator",      # tag de agente para el tool call
        client_id=str(user.get("id") or ""),
        max_results=request.max_results,
    )
    if not result.get("success"):
        err = str(result.get("error") or "unknown_research_error")
        if "BRAVE_API_KEY" in err:
            raise HTTPException(503, detail="brave_not_configured")
        if "Timeout" in err:
            raise HTTPException(503, detail="brave_timeout")
        if "Brave HTTP" in err:
            raise HTTPException(503, detail=f"brave_unavailable:{err}")
        raise HTTPException(500, detail=f"research_failed:{err[:200]}")
    # BUG fix: web_search_tool.py:97 retorna 'content' · ResearchResult
    # espera 'snippet' · ResearchResult(**r) hace Pydantic ValidationError
    # → FastAPI 500 (causa del bug reportado por owner). Mapeo explícito
    # robusto · tolera ambos shapes (legacy content + future snippet).
    safe = [x for x in (_safe_result(r) for r in (result.get("results") or [])) if x is not None]
    return ResearchResponse(
        query=str(result.get("query") or request.query),
        results=safe,
        answer=_safe_answer(result.get("answer")),
        count=len(safe),
        duration_ms=int(result.get("duration_ms") or 0),
    )
