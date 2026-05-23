"""Generate 1 or N text variations in parallel · Sprint 2 P2.

asyncio.gather() con 3 temperaturas (0.3 / 0.7 / 1.0) cuando n=3 · una sola
con 0.7 cuando n=1. Por cada variación exitosa: compute virality + insert draft
+ collect VariationItem. Si todas fallan retorna [] · handler convierte a 503.
Cache_control ephemeral en system hace cache HIT en calls 2 y 3 → costo ~1.5x.

FIX A (23 may 2026): Claude retorna JSON estructurado per spec del
content_creator persona ({"draft": "...", "hook": "...", "framework": ...}).
_extract_draft parsea + extrae solo el campo draft para el frontend ·
preserva raw_response[:500] en metadata para debug.
"""
import asyncio
import json
import re

from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateTextRequest, VariationItem,
)
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.domain.virality_score import compute_virality_score
from app.bc_cognition.infrastructure._anthropic_types import ClaudeResponse
from app.bc_cognition.infrastructure.anthropic_adapter import generate

_TEMP_TRIPLE = [(0.3, "A"), (0.7, "B"), (1.0, "C")]
_TEMP_SINGLE = [(0.7, "A")]
_UI_TO_DB_TYPE = {"caption": "text", "hashtags": "text", "video_script": "video"}
_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _extract_draft(raw: str) -> str:
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


async def generate_variations(
    system: str, request: GenerateTextRequest, dna: BrandDNA,
    client_id: str, n: int,
) -> list[VariationItem]:
    pairs = _TEMP_TRIPLE if n == 3 else _TEMP_SINGLE
    messages = [{"role": "user", "content": f"Tema: {request.topic}"}]
    coros = [
        generate(agent_code="content_creator", system=system, messages=messages,
                 max_tokens=1500, temperature=t)
        for t, _ in pairs
    ]
    results = await asyncio.gather(*coros)

    out: list[VariationItem] = []
    for (resp, err), (temp, label) in zip(results, pairs):
        if err or not resp:
            continue
        item = _persist_variation(resp, temp, label, request, dna, client_id)
        if item:
            out.append(item)
    return out


def _persist_variation(
    resp: ClaudeResponse, temp: float, label: str,
    request: GenerateTextRequest, dna: BrandDNA, client_id: str,
) -> VariationItem | None:
    clean_text = _extract_draft(resp.text)
    virality = compute_virality_score(clean_text, dna, request.platform)
    db_type = _UI_TO_DB_TYPE.get(request.content_type, "text")
    content_id = repo.safe_insert(
        f"insert_variation_{label}", repo.insert_generated_content, client_id, {
            "agent_code": "content_creator", "content_type": db_type,
            "prompt": request.topic, "generated_text": clean_text,
            "metadata": {
                "model": resp.model_used, "tokens": resp.input_tokens + resp.output_tokens,
                "cost_usd": resp.cost_usd, "ui_type": request.content_type,
                "platform": request.platform, "tone": request.tone,
                "brand_dna_score": dna.score, "brand_dna_label": dna.confidence_label(),
                "virality_score": virality["score"], "virality_breakdown": virality["breakdown"],
                "variation_label": label, "temperature": temp,
                "raw_response": resp.text[:500],
            },
            "confidence": 8, "status": "draft", "compliance_passed": True,
        },
    )
    if not content_id:
        return None
    return VariationItem(
        id=content_id, label=label, temperature=temp,
        generated_text=clean_text, virality_score=virality["score"],
        virality_estimated=True,
    )
