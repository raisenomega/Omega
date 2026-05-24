"""Sanitizer central de input no confiable · orquesta domain.input_threats (A9).

Spec: PROTOCOLO_SEGURIDAD_INPUT_OMEGA.md (firmado). Result-tuple (A5) · fail-closed:
ante error interno retorna SanitizerError y el caller rechaza (contexto alto riesgo).
"""
import logging
from dataclasses import dataclass
from app.bc_cognition.domain.input_threats import (
    InputContext, SanitizerAction, ThreatFlag, MAX_CHARS,
    normalize, redact_pii, scan_threats, is_ambiguous, decide,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SanitizedInput:
    clean_text: str
    action: SanitizerAction
    risk_score: int
    flags: tuple[ThreatFlag, ...]
    redactions: int


@dataclass(frozen=True)
class SanitizerError:
    code: str
    detail: str


def sanitize_input(
    text: str, context: InputContext,
) -> tuple[SanitizedInput | None, SanitizerError | None]:
    """Punto único de saneamiento de input no confiable. Cero raise (A5). Spec §3-4."""
    try:
        clean = normalize(text)
        had_control = clean != text
        capped = len(clean) > MAX_CHARS[context]
        clean = clean[:MAX_CHARS[context]]
        clean, redactions = redact_pii(clean)
        flags = scan_threats(clean, context)
        if redactions:
            flags.add(ThreatFlag.PII)
        if capped:
            flags.add(ThreatFlag.LENGTH)
        if had_control:
            flags.add(ThreatFlag.CONTROL_CHARS)
        action, risk = decide(frozenset(flags), is_ambiguous(clean))
        ordered = tuple(sorted(flags, key=lambda f: f.value))
        return SanitizedInput(clean, action, risk, ordered, redactions), None
    except Exception as exc:  # fail-closed · decisión §8.5
        logger.error(f"input_sanitizer failure (context={context}): {exc}", exc_info=True)
        return None, SanitizerError("sanitizer_failure", str(exc))
