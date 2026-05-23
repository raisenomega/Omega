"""Helpers para extraer campo 'draft' del response JSON de Claude.

Extraído de _variations.py (Sprint 1 paso preventivo · libera espacio para
vault selector + brand_dna_score). Spec: content_creator persona dice retornar
JSON estructurado · este módulo lo unwrap al texto limpio para frontend.
"""
import json
import re

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def extract_draft(raw: str) -> str:
    """Extrae 'draft' · prueba cleaned + substring entre llaves · fallback raw."""
    cleaned = _JSON_FENCE_RE.sub("", raw).strip()
    first, last = cleaned.find("{"), cleaned.rfind("}")
    candidates = [cleaned]
    if first >= 0 and last > first:
        candidates.append(cleaned[first:last + 1])
    for c in candidates:
        try:
            data = json.loads(c)
            if isinstance(data, dict) and isinstance(data.get("draft"), str):
                return data["draft"]
        except (json.JSONDecodeError, TypeError):
            continue
    return raw
