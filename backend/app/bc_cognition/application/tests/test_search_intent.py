"""Tests dominio search_intent · 4 casos (happy/edge/error/boundary). Auto-Brave-Search."""
from app.bc_cognition.domain.search_intent import needs_web_search, build_query, format_snippets


def test_happy_no_trigger_no_search():
    """Mensaje normal → no busca. 'hoy' amplio sin cue NO dispara (FP-guard)."""
    assert needs_web_search("¿qué publico hoy en Instagram?") is False
    assert needs_web_search("dame ideas de contenido para mi cafetería") is False
    # umbral subido 25 may: ya NO disparan en chat normal (evita +20s de Brave)
    assert needs_web_search("escribe el newsletter de esta semana") is False  # antes: "news"+"esta semana"
    assert needs_web_search("¿qué publico esta semana?") is False              # antes: "esta semana"


def test_edge_strong_trigger_fires_alone():
    """Términos fuertes ES/EN disparan solos."""
    assert needs_web_search("qué está pasando con mi competencia")
    assert needs_web_search("what's the latest news in my market")
    assert needs_web_search("dame el trending de esta semana")


def test_error_broad_term_needs_cue():
    """Amplios (hoy/reciente) solo con cue de búsqueda (umbral · owner)."""
    assert needs_web_search("lo hago hoy") is False
    assert needs_web_search("qué pasó hoy en el mercado")          # hoy + cue 'mercado'
    assert needs_web_search("noticias recientes de mi sector")     # 'noticias' fuerte


def test_boundary_query_and_snippets():
    """build_query (mensaje+vertical) + format_snippets (cap 500 · máx 3 · vacío→'')."""
    assert build_query("tendencias", "restaurante") == "tendencias restaurante"
    out = format_snippets(["x" * 800, "b", "c", "d"])
    assert "CONTEXTO WEB" in out and "· b" in out and "· c" in out and "· d" not in out  # máx 3
    assert ("x" * 500) in out and ("x" * 501) not in out  # cap 500
    assert format_snippets([]) == "" and format_snippets(["  "]) == ""
