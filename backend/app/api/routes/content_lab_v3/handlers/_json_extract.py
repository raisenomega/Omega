"""Helpers para extraer campo 'draft' del response JSON de Claude.

Extraído de _variations.py (Sprint 1 paso preventivo · libera espacio para
vault selector + brand_dna_score). Spec: content_creator persona dice retornar
JSON estructurado · este módulo lo unwrap al texto limpio para frontend.
"""
import json
import re

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def extract_draft(raw: str) -> str:
    """Extrae 'draft' · prueba cleaned + substring entre llaves + REPAIR de
    newlines literales que el modelo mete dentro de los strings (JSON inválido
    para json.loads estricto · BUG 11 jun) · fallback raw. Así el bloque
    pre-flight/meta NO se filtra como caption cuando el modelo lo antepone."""
    cleaned = _JSON_FENCE_RE.sub("", raw).strip()
    first, last = cleaned.find("{"), cleaned.rfind("}")
    candidates = [cleaned]
    if first >= 0 and last > first:
        region = cleaned[first:last + 1]
        candidates.append(region)
        # wrap del modelo = newlines LITERALES (los \n intencionales son escapes
        # de 2 chars, no se tocan) → colapsar a espacio vuelve el JSON parseable.
        candidates.append(region.replace("\n", " "))
    for c in candidates:
        try:
            data = json.loads(c)
            if isinstance(data, dict) and isinstance(data.get("draft"), str):
                return data["draft"]
        except (json.JSONDecodeError, TypeError):
            continue
    return raw
