"""Application · scorer de voz de marca para el gate X5 (Opción A · refinamiento 3).

Compone marca comprimida + contenido y pide a Claude (Haiku vía routing_table
"brand_voice_checker" · I2) un score 0-1. NUNCA llama al SDK directo: usa el
anthropic_adapter (I10). Result tuple (A5): (ok, {score, reasons}, err).
err="brand_voice_check_unavailable" si el ref o el adapter fallan → el gate
decide 503 honesto o, con force, agendar bajo responsabilidad humana."""
import json
import logging
from typing import Any, Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.application.use_brand_voice_summary import build_brand_voice_summary
from app.bc_cognition.domain.brand_voice_scorer_prompt import SYSTEM, build_user_prompt

logger = logging.getLogger(__name__)

_UNAVAILABLE = "brand_voice_check_unavailable"


def has_brand_reference(client_id: str) -> bool:
    """Determinístico (sin Haiku) · True si el cliente tiene voz de marca
    definida (corpus, keywords o ejemplos). False → el gate X5 no puede medir
    desviación de una voz indefinida → PASS con rastro. Ante error de lectura
    devuelve True (fail-safe hacia proteger: que el scorer decida/503)."""
    try:
        ref = build_brand_voice_summary(client_id)
    except Exception as e:
        logger.warning("has_brand_reference: ref load failed (client=%s): %s", client_id, e)
        return True
    return bool(ref.get("corpus_count") or ref.get("top_keywords") or ref.get("latest_approvals"))


def _parse_score(text: str) -> Optional[dict[str, Any]]:
    """Extrae {score, reasons} del JSON del modelo · None si no parsea (I7)."""
    try:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end < 0:
            return None
        data = json.loads(text[start:end + 1])
        score = max(0.0, min(1.0, float(data["score"])))
        reasons = [str(r) for r in (data.get("reasons") or [])][:5]
        return {"score": score, "reasons": reasons}
    except (ValueError, KeyError, TypeError):
        return None


async def score_brand_voice(client_id: str, content_text: str):
    """(True, {score, reasons}, None) | (False, None, 'brand_voice_check_unavailable')."""
    try:
        brand_ref = build_brand_voice_summary(client_id)
    except Exception as e:  # ref load falla → check no disponible (no se inventa)
        logger.warning("brand_voice ref load failed (client=%s): %s", client_id, e)
        return (False, None, _UNAVAILABLE)

    response, error = await generate(
        agent_code="brand_voice_checker",
        system=SYSTEM,
        messages=[{"role": "user", "content": build_user_prompt(content_text, brand_ref)}],
        max_tokens=300,
        temperature=0.0,
    )
    if error is not None or response is None:
        logger.warning("brand_voice scorer unavailable: %s", error)
        return (False, None, _UNAVAILABLE)
    parsed = _parse_score(response.text)
    if parsed is None:
        logger.warning("brand_voice scorer JSON ilegible: %.120s", response.text)
        return (False, None, _UNAVAILABLE)
    return (True, parsed, None)
