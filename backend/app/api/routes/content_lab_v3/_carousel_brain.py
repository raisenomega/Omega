"""Pieza 1 · A1.2 · Cerebro del carrusel: genera el GUION estructurado (NO imágenes · eso es A2).

Capa APARTE de RAFA: system prompt PROPIO (NO el prompt_vault de RAFA · NO personas/). Fuerza
tool-use vía tool_choice (A1.1, en prod) para GARANTIZAR slides[{text, visual_note}]. Patrón
copiado de _aria_tools (parsea block.input). agent_code='content_creator' solo elige el modelo
(Sonnet) por routing · NO usa la persona de RAFA (pasamos nuestro propio system).

Garantía de 3 capas: (1) tool_choice forzado + (2) required en el schema + (3) BACKSTOP de código
(abajo): nunca un carrusel con <3 placas ni una placa sin visual_note (P1).
"""
from typing import Any

from app.api.routes.content_lab_v3._carousel_context import build_user_message as _build_user_message
from app.bc_cognition.infrastructure.anthropic_adapter import generate

_MIN_SLIDES = 3
_MAX_SLIDES = 10  # D5 · cap DURO por código (el schema solo sugiere · el modelo no lo respeta hard)
_TOOL_CHOICE: dict[str, Any] = {"type": "tool", "name": "emit_carousel_script"}

CAROUSEL_TOOL: dict[str, Any] = {
    "name": "emit_carousel_script",
    "description": "Emite el guion estructurado de un carrusel de placas de diseño (texto, no imágenes).",
    "input_schema": {
        "type": "object",
        "properties": {
            "carousel_title": {"type": "string", "description": "Título/tema · base del caption del post."},
            "slides": {
                "type": "array", "minItems": _MIN_SLIDES, "maxItems": _MAX_SLIDES,
                "items": {
                    "type": "object",
                    "properties": {
                        "order": {"type": "integer", "description": "1..N · orden de swipe."},
                        "slide_type": {"type": "string", "enum": ["portada", "punto", "cierre", "cta"]},
                        "text": {"type": "string", "description": "Copy EN la placa · ESPAÑOL · conciso · tono del cliente."},
                        "visual_note": {"type": "string", "description": (
                            "Instrucción CORTA en INGLÉS para el generador de imagen: fondo, layout, "
                            "posición del texto, estilo, formas. NO narrativo, NO el copy, NO colores.")},
                    },
                    "required": ["text", "visual_note"],
                },
            },
        },
        "required": ["carousel_title", "slides"],
    },
}

SYSTEM = (
    "Sos el diseñador de guiones de carrusel de OMEGA. Generás una SERIE COHERENTE de placas de SOLO "
    "DISEÑO: fondo + texto + formas geométricas. CERO personajes, CERO rostros, CERO fotos de gente.\n\n"
    "Cada placa tiene:\n"
    "- text: el copy que el lector ve EN la placa, en ESPAÑOL, en el tono del cliente, conciso.\n"
    "- visual_note: instrucción CORTA (<=120 chars) en INGLÉS e INSTRUCTIVA para el generador de imagen. "
    "Describí: fondo, layout, posición del texto, estilo, formas de acento. "
    "Ejemplo BUENO: 'dark background, large bold headline top-left, geometric accent shapes bottom-right, minimal'. "
    "Ejemplo MALO: 'una imagen que transmita confianza'. "
    "NO incluyas colores (la paleta de marca se agrega aparte). NO repitas el copy dentro del visual_note.\n\n"
    "COHERENCIA: todas las placas comparten el mismo sistema visual (familia de layout); el contenido "
    "evoluciona: portada (gancho) -> puntos -> cierre/CTA.\n"
    "Usá la herramienta emit_carousel_script SIEMPRE."
)


class CarouselScriptError(Exception):
    """Backstop · el guion del modelo no cumple el contrato mínimo (P1: nunca un carrusel inválido)."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


async def generate_carousel_script(idea: str, ctx: dict[str, Any], n_slides: int) -> dict[str, Any]:
    """Devuelve {carousel_title, slides:[...]} GARANTIZADO, o lanza CarouselScriptError (backstop · capa 3)."""
    user_msg = _build_user_message(idea, ctx, n_slides)
    resp, err = await generate(
        agent_code="content_creator",  # routing → Sonnet · NO la persona RAFA (system es nuestro)
        system=SYSTEM, messages=[{"role": "user", "content": user_msg}],
        max_tokens=2048, tools=[CAROUSEL_TOOL], tool_choice=_TOOL_CHOICE,
    )
    if err is not None or resp is None:
        raise CarouselScriptError(err.code if err else "no_response")
    if not resp.tool_calls:
        raise CarouselScriptError("no_tool_call")  # raro con tool_choice forzado · honesto si pasa
    data = getattr(resp.tool_calls[0], "input", {}) or {}
    slides = list(data.get("slides") or [])
    if len(slides) > _MAX_SLIDES:
        slides = slides[:_MAX_SLIDES]  # D5 · recorte amable por código (no rechazo)
    if len(slides) < _MIN_SLIDES:
        raise CarouselScriptError("too_few_slides")
    for s in slides:
        if not str(s.get("visual_note") or "").strip():
            raise CarouselScriptError("empty_visual_note")  # P1 · ninguna placa sin guía visual
    return {"carousel_title": str(data.get("carousel_title") or ""), "slides": slides}
