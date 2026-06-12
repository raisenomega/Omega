"""Dominio · criterios y prompt del scorer de voz de marca (gate X5).

Puro (A2): solo stdlib. El scorer (application) compone el user prompt con el
texto del contenido + un resumen compacto de la marca (I6 ≤2000 tok) y exige
salida JSON estructurada (I7) {score, reasons}. El score 0.0-1.0 mide qué tan
bien encaja el contenido con la voz de la marca del cliente (P2 = activo)."""
import json
from typing import Any

# Umbrales del gate X5 · damage gate de dos bandas. Calibración 11 jun (corpus
# real afb9f578 · n=1 cliente · escala anclada): legítimo ≥0.62 (captions 0.62-0.78,
# hashtags legítimos 0.62) · dañino ≤0.15 (insultos, spam, off-tone). La división
# real es ~0.5, NO 0.7 → bloquear solo el daño, marcar lo genérico sin bloquear.
# Re-validar con ≥3 clientes (DEBT-X5-CALIBRATION-MULTICLIENT).
SCORE_BLOCK_THRESHOLD = 0.5  # < esto = DAÑA la marca (insultos/spam/off-tone) → 422
SCORE_BRAND_BAR = 0.7        # 0.5–0.7 = genérico/no-daña → PASA con flag below_brand_bar

SYSTEM = (
    "Eres el verificador de voz de marca de OmegaRaisen. Evalúas si un "
    "contenido respeta la voz de la marca del cliente (tono, vocabulario, "
    "palabras aprobadas, consistencia). Devuelves SOLO un objeto JSON "
    '{"score": number 0.0-1.0, "reasons": [string, ...]} sin texto extra.\n'
    "ESCALA ANCLADA (calibrá SIEMPRE contra los EJEMPLOS APROBADOS del cliente):\n"
    "• 0.9-1.0 = indistinguible de la voz de marca.\n"
    "• 0.7-0.85 = consistente con la marca, publicable sin retoque.\n"
    "• 0.5-0.65 = neutro/genérico: no daña la marca pero no suena a ella.\n"
    "• <0.5 = contradice o DAÑA la voz (off-tone, insultos, claims falsos).\n"
    "Si el contenido iguala el tono/energía/vocabulario de los ejemplos "
    "aprobados, merece 0.7+; NO lo castigues a <0.7 por matices menores ni por "
    "faltar UNA keyword. Reservá <0.5 para contenido que DAÑA la marca. Ejemplo "
    "BAJO (~0.2): 'Estimado cliente, le ofrecemos la mejor solución del mercado. "
    "Contáctenos.' (corporativo, genérico, sin la voz). Sé honesto pero justo: "
    "la marca del cliente es el activo (P2). Máximo 4 razones BREVES (1 línea c/u)."
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
