"""Dominio · criterios y prompt del scorer de voz de marca (gate X5).

Puro (A2): solo stdlib. El scorer (application) compone el user prompt con el
texto del contenido + un resumen compacto de la marca (I6 ≤2000 tok) y exige
salida JSON estructurada (I7) {score, reasons}. El score 0.0-1.0 mide qué tan
bien encaja el contenido con la voz de la marca del cliente (P2 = activo)."""
import json
from typing import Any

MIN_SCORE = 0.7  # X5: ningún draft pasa a scheduled con match_score < 0.7

SYSTEM = (
    "Eres el verificador de voz de marca de OmegaRaisen. Evalúas si un "
    "contenido respeta la voz de la marca del cliente (tono, vocabulario, "
    "palabras aprobadas, consistencia). Devuelves SOLO un objeto JSON "
    '{"score": number 0.0-1.0, "reasons": [string, ...]} sin texto extra. '
    "score = qué tan bien encaja el contenido con la marca (1.0 = calce "
    "perfecto · 0.0 = fuera de tono). Sé honesto y estricto: la marca del "
    "cliente es el activo (P2). Máximo 4 razones BREVES (1 línea cada una)."
)


def build_user_prompt(content_text: str, brand_ref: dict[str, Any]) -> str:
    """User message · marca comprimida (I6) + contenido a evaluar."""
    ref = {
        "corpus_count": brand_ref.get("corpus_count", 0),
        "top_keywords": [k.get("keyword") if isinstance(k, dict) else k
                         for k in (brand_ref.get("top_keywords") or [])][:12],
        "ejemplos_aprobados": (brand_ref.get("latest_approvals") or [])[:3],
    }
    return (
        "MARCA DEL CLIENTE (referencia):\n"
        + json.dumps(ref, ensure_ascii=False)
        + "\n\nCONTENIDO A EVALUAR:\n"
        + content_text.strip()
        + '\n\nDevuelve el JSON {"score", "reasons"}.'
    )
