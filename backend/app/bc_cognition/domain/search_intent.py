"""Intención de búsqueda web · capa pura (A2). Trigger heurístico + query + formato.

Auto-Brave-Search: detecta si un mensaje requiere info actual del mundo real.
Términos amplios (hoy/reciente/ahora) SOLO disparan con un cue de búsqueda (umbral
subido · decisión owner). Frases multi-palabra y términos fuertes disparan solos.
Bilingüe ES/EN. Cero imports externos.
"""
from typing import Final, List

_STRONG: Final = (
    "trending", "qué está pasando", "que esta pasando", "última hora", "ultima hora",
    "ahora mismo", "esta semana", "noticias", "competencia", "competidor", "tendencia",
    "novedades",
    "what's happening", "whats happening", "breaking news", "right now", "this week",
    "news", "competitor", "trend", "latest news",
)
_BROAD: Final = (
    "hoy", "today", "reciente", "recientemente", "recent", "recently",
    "ahora", "now", "actual", "current", "currently",
)
_CUE: Final = (
    "busca", "buscar", "buscá", "search", "noticia", "news", "tendencia", "trend",
    "competen", "mercado", "market", "pasando", "evento", "novedad",
)


def needs_web_search(text: str) -> bool:
    """True si pide info actual. Amplios solo con cue (FP-guard · decisión owner)."""
    t = text.lower()
    if any(s in t for s in _STRONG):
        return True
    return any(b in t for b in _BROAD) and any(c in t for c in _CUE)


def build_query(message: str, vertical: str) -> str:
    """Query Brave = mensaje + vertical del cliente · capado a 200 chars."""
    q = f"{message} {vertical}".strip() if vertical else message.strip()
    return q[:200]


def format_snippets(snippets: List[str], cap: int = 500, max_n: int = 3) -> str:
    """Bloque de contexto web · máx max_n snippets · cap chars c/u. Externo → verificar."""
    items = [s.strip()[:cap] for s in snippets if s.strip()][:max_n]
    if not items:
        return ""
    body = "\n".join(f"· {s}" for s in items)
    return "# CONTEXTO WEB ACTUAL (Brave · fuentes externas · verificá antes de afirmar)\n" + body
