"""Modelo de amenazas de input LLM · capa pura (A2). Tipos + patrones + detectores.

Spec: PROTOCOLO_SEGURIDAD_INPUT_OMEGA.md (firmado 24 may 2026). Capa 1 heurística
(Haiku diferido a Sprint 5). Cero imports externos.
"""
import re
import unicodedata
from enum import Enum
from types import MappingProxyType
from typing import Final


class InputContext(Enum):
    ARIA_CHAT = "aria_chat"
    CONTENT_PROMPT = "content_prompt"
    UPLOADED_DOCUMENT = "uploaded_document"
    RESEARCH_SNIPPET = "research_snippet"
    BRAND_CORPUS = "brand_corpus"


class SanitizerAction(Enum):
    ALLOW = "allow"
    REDACTED = "redacted"
    HOLD_FOR_HUMAN_REVIEW = "hold_for_human_review"
    BLOCK = "block"


class ThreatFlag(Enum):
    INJECTION = "T1"; INDIRECT = "T2"; JAILBREAK = "T3"
    PII = "T4"; LENGTH = "T5"; CONTROL_CHARS = "T6"; EXFIL = "T7"


MAX_CHARS: Final[MappingProxyType] = MappingProxyType({
    InputContext.ARIA_CHAT: 2000, InputContext.CONTENT_PROMPT: 1000,
    InputContext.UPLOADED_DOCUMENT: 10000, InputContext.RESEARCH_SNIPPET: 500,
    InputContext.BRAND_CORPUS: 3000,
})

_INDIRECT_CTX: Final = frozenset({InputContext.UPLOADED_DOCUMENT, InputContext.RESEARCH_SNIPPET})
_BLOCK_FLAGS: Final = frozenset({ThreatFlag.INJECTION, ThreatFlag.INDIRECT, ThreatFlag.JAILBREAK, ThreatFlag.EXFIL})
_KEEP_CTRL: Final = frozenset({"\n", "\t", "\r"})

_INJECTION: Final = re.compile(r"(ignor\w*|olvid\w*|forget|disregard|override).{0,30}(previous|prior|anterior|instruc|reglas|rules)|(a partir de ahora|from now on|ahora sos|you are now|act as|pretend you are)|<!--[^>]*?(system|assistant|instruc|aprob|approve|ignor|bypass)[^>]*?-->", re.I)
_JAILBREAK: Final = re.compile(r"\b(dev\s*mode|do anything now|\bdan\b|jailbreak)\b|sin\s+(ninguna\s+)?restric\w*|(decod\w*|decode|ejecut\w*|execute|base64)\b.{0,15}[A-Za-z0-9+/]{16,}={0,2}", re.I)
_EXFIL: Final = re.compile(r"(reveal|revel\w*|repeat|repet\w*|print|mostr\w*|imprim\w*|dump).{0,25}(system\s*prompt|tus?\s+instruc|word.for.word|palabra por palabra)", re.I)
_AMBIGUOUS: Final = re.compile(r"hipot[eé]tic|hypothetic|imagin[aá]|pretend\b|role.?play|si no tuvieras|fines educativos|educational purposes", re.I)
_PII: Final = (
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "[CARD]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"(?<!\w)\+?\d[\d ()-]{8,16}\d(?!\w)"), "[PHONE]"),
)


def normalize(text: str) -> str:
    """NFKC (anti-homoglyph) + strip de control/zero-width/RTL chars, conserva \\n\\t\\r (T6)."""
    nfkc = unicodedata.normalize("NFKC", text)
    return "".join(c for c in nfkc if c in _KEEP_CTRL or unicodedata.category(c) not in ("Cc", "Cf"))


def redact_pii(text: str) -> tuple[str, int]:
    """Reemplaza PII por placeholders → (texto, n_redacciones) (T4)."""
    total = 0
    for pat, tag in _PII:
        text, n = pat.subn(tag, text)
        total += n
    return text, total


def scan_threats(text: str, context: InputContext) -> set[ThreatFlag]:
    """Detecta T1/T2/T3/T7 (alta confianza). INDIRECT si el contexto es doc/research."""
    indirect = context in _INDIRECT_CTX
    found: set[ThreatFlag] = set()
    if _INJECTION.search(text):
        found.add(ThreatFlag.INDIRECT if indirect else ThreatFlag.INJECTION)
    if _JAILBREAK.search(text):
        found.add(ThreatFlag.INDIRECT if indirect else ThreatFlag.JAILBREAK)
    if _EXFIL.search(text):
        found.add(ThreatFlag.EXFIL)
    return found


def is_ambiguous(text: str) -> bool:
    """Señales de jailbreak de baja confianza → HOLD (T3 ambiguo)."""
    return bool(_AMBIGUOUS.search(text))


def decide(flags: frozenset[ThreatFlag], ambiguous: bool) -> tuple[SanitizerAction, int]:
    """flags → (acción, risk 0-10). Prioridad BLOCK > HOLD > REDACTED > ALLOW (P2/P3)."""
    if flags & _BLOCK_FLAGS:
        return SanitizerAction.BLOCK, 9
    if ambiguous:
        return SanitizerAction.HOLD_FOR_HUMAN_REVIEW, 6
    if flags:
        return SanitizerAction.REDACTED, 3
    return SanitizerAction.ALLOW, 0
