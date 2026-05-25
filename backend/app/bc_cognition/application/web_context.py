"""Auto-Brave-Search · orquesta detección + búsqueda + saneo + formato (application).

fetch_web_context: si el texto pide info actual → web_search → sanea cada snippet
(RESEARCH_SNIPPET · cierra T2 · 4A-3 #2) → bloque cap 3×500. Best-effort: error/fallo → "".
"""
import logging
from typing import Optional
from app.bc_cognition.domain.search_intent import build_query, format_snippets, needs_web_search
from app.bc_cognition.domain.input_threats import InputContext, SanitizerAction
from app.bc_cognition.application.input_sanitizer import sanitize_input
from app.infrastructure.tools.web_search_tool import web_search

logger = logging.getLogger(__name__)
_UNSAFE = (SanitizerAction.BLOCK, SanitizerAction.HOLD_FOR_HUMAN_REVIEW)


async def fetch_web_context(message: str, vertical: str, agent_code: str, client_id: Optional[str]) -> str:
    """Bloque de contexto web actual (o "" si no aplica/falla). Snippets saneados (T2)."""
    if not needs_web_search(message):
        return ""
    try:
        result = await web_search(build_query(message, vertical), agent_code, client_id, max_results=3)
        if not result.get("success"):
            return ""
        clean = []
        for r in result.get("results", []):
            out, err = sanitize_input(str(r.get("content") or ""), InputContext.RESEARCH_SNIPPET)
            if err is None and out is not None and out.action not in _UNSAFE:
                clean.append(out.clean_text)
        return format_snippets(clean)
    except Exception as exc:  # best-effort · una búsqueda fallida no rompe el flujo
        logger.error(f"fetch_web_context failed: {exc}", exc_info=True)
        return ""
