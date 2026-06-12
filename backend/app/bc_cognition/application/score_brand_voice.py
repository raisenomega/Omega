"""Application · scorer de voz de marca para el gate X5 (Opción A).

Haiku vía routing_table "brand_voice_checker" (I2) · anthropic_adapter, NUNCA
SDK directo (I10) · Result (A5): (ok, {score, reasons}, err). err=
"brand_voice_check_unavailable" si el ref o el adapter fallan."""
import json
import logging
import re
from typing import Any, Optional

from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_cognition.application.use_brand_voice_summary import build_brand_voice_summary
from app.bc_cognition.domain.brand_voice_scorer_prompt import SYSTEM, build_user_prompt

logger = logging.getLogger(__name__)

_UNAVAILABLE = "brand_voice_check_unavailable"


def has_brand_reference(client_id: str) -> bool:
    """Determinístico · True si hay voz definida (corpus/keywords/ejemplos).
    False → PASS con rastro (no se mide una voz indefinida). Error de lectura →
    True (fail-safe: que el scorer decida/503)."""
    try:
        ref = build_brand_voice_summary(client_id)
    except Exception as e:
        logger.warning("has_brand_reference: ref load failed (client=%s): %s", client_id, e)
        return True
    return bool(ref.get("corpus_count") or ref.get("top_keywords") or ref.get("latest_approvals"))


def _clamp(v: int | float | str) -> float:
    return max(0.0, min(1.0, float(v)))


def _parse_score(text: str) -> Optional[dict[str, Any]]:
    """Extrae {score, reasons} (I7). Tolera respuesta TRUNCADA (Haiku corta el
    array reasons al límite de tokens · 11 jun): el score viene primero → el
    fallback por regex lo rescata aunque falte el cierre del JSON."""
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start:end + 1])
            if isinstance(data, dict) and "score" in data:
                reasons = [str(r) for r in (data.get("reasons") or [])][:5]
                return {"score": _clamp(data["score"]), "reasons": reasons}
        except (ValueError, KeyError, TypeError):
            pass
    m = re.search(r'"score"\s*:\s*(-?\d+(?:\.\d+)?)', text)
    return {"score": _clamp(m.group(1)), "reasons": []} if m else None


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
        max_tokens=600,
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
