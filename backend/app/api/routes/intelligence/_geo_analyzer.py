"""Analizador GEO/AEO · visibilidad del negocio en búsquedas con IA.

Brave (web_search) recoge resultados del vertical+ciudad · Claude (sonnet,
agent_code='intelligence') determina si el negocio aparece. Sin DB · honesto:
si Brave no devuelve nada → ok=False con error claro · nunca crashea el parseo.
"""
from typing import Any, Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate as claude_generate
from app.infrastructure.tools.web_search_tool import format_for_claude, web_search

_SYSTEM = (
    "Sos un analista de visibilidad en buscadores con IA. Determiná si un "
    "negocio aparece en resultados de búsqueda de su industria/ciudad."
)
_STATUS_MAP = {
    "APPEARED": "appeared",
    "PARTIAL": "partial",
    "NOT_APPEARED": "not_appeared",
}


def _build_queries(industry: str, region: str) -> list[str]:
    if region:
        return [f"mejores {industry} en {region}", f"{industry} {region} recomendados"]
    return [f"mejores {industry}", f"{industry} recomendados"]


def _parse_geo_response(text: str) -> dict[str, Any]:
    """Parseo defensivo · nunca crashea. status/summary/tips desde el texto crudo."""
    lines = [ln.strip() for ln in (text or "").splitlines()]
    nonempty = [ln for ln in lines if ln]
    status = "unknown"
    if nonempty:
        status = _STATUS_MAP.get(nonempty[0].upper(), "unknown")
    summary: Optional[str] = None
    for ln in nonempty[1:]:
        if not ln.startswith("- "):
            summary = ln
            break
    tips = [ln[2:].strip() for ln in nonempty if ln.startswith("- ") and ln[2:].strip()]
    return {"status": status, "summary": summary, "tips": tips}


async def check_geo_visibility(
    business_name: str, industry: str, region: str, website: Optional[str]
) -> dict[str, Any]:
    """Verifica visibilidad GEO del negocio · dict {ok, ...}."""
    queries = _build_queries(industry, region)
    brave_blocks: list[str] = []
    total_results = 0
    for q in queries:
        try:
            res = await web_search(q, agent_code="intelligence", max_results=5)
        except Exception:
            continue
        total_results += res.get("count", 0) if res.get("success") else 0
        brave_blocks.append(format_for_claude(res))

    if total_results == 0:
        return {"ok": False, "error": "Brave Search no devolvió resultados"}

    user = (
        f"Negocio: {business_name}\nWebsite: {website or 'N/A'}\n"
        f"Industria: {industry}\nRegión: {region or 'N/A'}\n\n"
        "Resultados de búsqueda encontrados:\n" + "\n\n".join(brave_blocks) + "\n\n"
        "Respondé EXACTAMENTE en la primera línea uno de: "
        "APPEARED | PARTIAL | NOT_APPEARED. Luego una línea de resumen. "
        "Luego 2-4 tips concretos (uno por línea, empezando con '- ')."
    )
    resp, err = await claude_generate(
        agent_code="intelligence", system=_SYSTEM,
        messages=[{"role": "user", "content": user}],
        max_tokens=500, temperature=0.4,
    )
    if err is not None or resp is None:
        return {"ok": False, "error": err.code if err else "sin_respuesta"}

    parsed = _parse_geo_response(resp.text)
    return {"ok": True, "queries": queries, **parsed}
