"""Pieza 1 · contexto RICO del negocio → user_message del cerebro del carrusel (DEBT-CAROUSEL-THIN-CONTEXT).

RAFA escribía "de chiripa": el guion solo veía niche/audiencia/tono/nombre. Acá forwardeamos los campos
del onboarding que SÍ mueven la calidad del copy — sobre todo `business_what` (qué ofrece el negocio).

P1 · calidad de contexto, NO volumen: campos RELEVANTES (no las 30 columnas) + truncado por campo para
proteger el presupuesto (~2000 tokens). Vacíos se OMITEN (ni label huérfano ni el literal "None").
Extraído de _carousel_brain por C4 (el cerebro estaba en el techo de 100 líneas).
"""
from typing import Any

_MAX_FIELD = 280  # tope por campo de texto libre · acota el costo del contexto sin matar la señal

# (clave en client_context/clients, label español) · orden = prioridad para el modelo (qué ofrece arriba)
_FIELDS: tuple[tuple[str, str], ...] = (
    ("client_name", "Cliente"),
    ("niche", "Nicho"),
    ("business_what", "Qué ofrece"),
    ("business_diff", "Diferenciador"),
    ("business_to_whom", "A quién"),
    ("target_audience", "Audiencia"),
    ("tone", "Tono"),
    ("brand_voice", "Voz de marca"),
    ("content_themes", "Temas"),
    ("primary_goal", "Objetivo"),
    ("avoided_topics", "Evitar temas"),
    ("avoided_words", "Evitar palabras"),
    ("custom_instructions", "Instrucciones del cliente"),
)


def _fmt(val: object) -> str:
    """Normaliza un valor de contexto a texto legible y ACOTADO. Devuelve '' si vacío (se omite).
    `object` (no Any · C1): los isinstance de abajo estrechan el tipo de cada rama del jsonb."""
    if val is None:
        return ""
    if isinstance(val, list):  # jsonb array (content_themes, avoided_words) → lista separada por comas
        items = [str(x).strip() for x in val if str(x).strip()]
        return ", ".join(items)[:_MAX_FIELD]
    if isinstance(val, dict):  # brand_voice jsonb · suele ser {keywords:[...]}
        kws = val.get("keywords")
        if isinstance(kws, list) and kws:
            return ", ".join(str(x).strip() for x in kws if str(x).strip())[:_MAX_FIELD]
        flat = ", ".join(f"{k}: {v}" for k, v in val.items() if v)
        return flat[:_MAX_FIELD]
    return str(val).strip()[:_MAX_FIELD]


def build_user_message(idea: str, ctx: dict[str, Any], n_slides: int) -> str:
    """Mensaje al modelo del cerebro: idea + N + el contexto RICO del negocio (campos vacíos omitidos)."""
    parts = [f"Idea del carrusel: {idea}", f"Cantidad de placas: {n_slides}"]
    for key, label in _FIELDS:
        v = _fmt(ctx.get(key))
        if v:
            parts.append(f"{label}: {v}")
    return "\n".join(parts)
