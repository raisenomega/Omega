"""Analizador AEO · Answer Engine Optimization (≠ GEO).

Identifica las preguntas frecuentes del vertical (Brave = retrieval) y evalúa si
el sitio del negocio las responde (Claude sonnet, agent_code='intelligence', señales
del scraper). Sin DB · honesto: si Brave no devuelve nada → ok=False · parseo puro
defensivo que nunca crashea. I1: Brave=retrieval, Claude=Anthropic · sin otro proveedor.
"""
from typing import Any, Optional

from app.api.routes.intelligence._web_scraper import analyze_website
from app.bc_cognition.infrastructure.anthropic_adapter import generate as claude_generate
from app.infrastructure.tools.web_search_tool import format_for_claude, web_search

_SYSTEM = (
    "Sos un analista de Answer Engine Optimization (AEO). Identificás las preguntas "
    "frecuentes que hace la audiencia de una industria y evaluás si el sitio del "
    "negocio las responde."
)
_HEADERS = {
    "PREGUNTAS:": "questions",
    "RESPONDE:": "answered",
    "GAPS:": "gaps",
    "TIPS:": "tips",
}


def _parse_aeo_response(text: str) -> dict[str, Any]:
    """Parseo defensivo · nunca crashea. Secciones por header · líneas '- '."""
    out: dict[str, list[str]] = {"questions": [], "answered": [], "gaps": [], "tips": []}
    current: Optional[str] = None
    for raw in (text or "").splitlines():
        ln = raw.strip()
        if not ln:
            continue
        header = _HEADERS.get(ln.upper())
        if header is not None:
            current = header
            continue
        if current is not None and ln.startswith("- ") and ln[2:].strip():
            out[current].append(ln[2:].strip())
    return out


def _site_signals(site: dict[str, Any]) -> str:
    """Resumen de señales del sitio para el prompt · vacío si no hay scrape ok."""
    if not site.get("ok"):
        return ""
    parts = [
        f"Title: {site.get('title', '')}",
        f"Meta: {site.get('meta_description', '')}",
        f"H1: {', '.join(site.get('h1', []))}",
        f"H2: {', '.join(site.get('h2', []))}",
        f"H3: {', '.join(site.get('h3', []))}",
        f"Keywords: {', '.join(site.get('keywords', []))}",
    ]
    return "\n".join(parts)


async def check_aeo(
    business_name: str, industry: str, region: str, website: Optional[str]
) -> dict[str, Any]:
    """Analiza AEO del negocio · dict {ok, questions, answered, gaps, tips}."""
    queries = [
        f"preguntas frecuentes {industry}",
        f"{industry} qué necesito saber",
    ]
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

    site_block = ""
    if website:
        site = await analyze_website(website)
        site_block = _site_signals(site)

    user = (
        f"Negocio: {business_name}\nIndustria: {industry}\n"
        f"Región: {region or 'N/A'}\n\n"
        "Resultados de búsqueda del vertical:\n" + "\n\n".join(brave_blocks) + "\n\n"
        "Señales del sitio del negocio:\n" + (site_block or "Sin señales del sitio.") + "\n\n"
        "Devolvé en líneas: primero 'PREGUNTAS:' y 3-6 preguntas (una por línea "
        "con '- '). Luego 'RESPONDE:' con las que el sitio cubre ('- '). Luego "
        "'GAPS:' con las que faltan ('- '). Luego 'TIPS:' con 2-4 consejos ('- ')."
    )
    resp, err = await claude_generate(
        agent_code="intelligence", system=_SYSTEM,
        messages=[{"role": "user", "content": user}],
        max_tokens=700, temperature=0.4,
    )
    if err is not None or resp is None:
        return {"ok": False, "error": err.code if err else "sin_respuesta"}

    parsed = _parse_aeo_response(resp.text)
    return {"ok": True, **parsed}
