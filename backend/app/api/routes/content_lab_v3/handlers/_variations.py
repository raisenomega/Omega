"""Generate 1 or N text variations in parallel · Sprint 2 P2.

asyncio.gather() con 3 temperaturas (0.4 / 0.7 / 0.9) cuando n=3 · una sola
con 0.7 cuando n=1. Cada variación A/B/C appendea su directiva de tono al USER
MESSAGE (no al system → no rompe cache). Por cada variación exitosa: compute
virality + insert draft + collect VariationItem. Si todas fallan retorna [] ·
handler convierte a 503.
Cache_control ephemeral en system hace cache HIT en calls 2 y 3 → costo ~1.5x.

Sprint 1 Subtarea 1.2: user_message viene formateado del handler (vault prompt
con placeholders resueltos · o 'Tema: ...' fallback si no hay match en vault).
"""
import asyncio

from app.api.routes.content_lab_v3 import _content_lab_repository as repo
from app.api.routes.content_lab_v3.handlers._json_extract import extract_draft
from app.api.routes.content_lab_v3.models.content_lab_models import (
    GenerateTextRequest, VariationItem,
)
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.domain.virality_score import compute_virality_score
from app.bc_cognition.infrastructure._anthropic_types import ClaudeResponse
from app.bc_cognition.infrastructure.anthropic_adapter import generate
from app.bc_billing.application.credits_service import debit

# Directivas de tono por variación · van al USER MESSAGE (varían sin romper el
# cache_control ephemeral del system · DEBT-TONO).
_DIR_A = ("TONO DE ESTA VERSIÓN: prudente, mesurado, profesional. "
          "Priorizá claridad y confianza sobre impacto.")
_DIR_B = ("TONO DE ESTA VERSIÓN: equilibrado — expresivo donde el tema lo "
          "permite, mesurado donde conviene. Ni tímido ni extremo.")
_DIR_C = ("TONO DE ESTA VERSIÓN: audaz, provocador, con opinión definida y "
          "ganchos fuertes — SOSTENIDO DE PRINCIPIO A FIN, no solo en la primera "
          "frase. Empujá los límites del Brand DNA: usá su vocabulario y sus "
          "referencias, pero NO suavices el atrevimiento para 'caber' en su tono "
          "habitual. Si la marca habitual es mesurada, tu trabajo es mostrar cómo "
          "suena su voz cuando se anima a romper.")
# (temperatura, label, directiva_de_tono)
_TEMP_TRIPLE = [(0.4, "A", _DIR_A), (0.7, "B", _DIR_B), (0.9, "C", _DIR_C)]
_TEMP_SINGLE = [(0.7, "A", "")]  # n=1: sin directiva · comportamiento actual intacto
_BY_LABEL = {lbl: (t, d) for t, lbl, d in _TEMP_TRIPLE}  # A/B/C → (temp, directiva)
_UI_TO_DB_TYPE = {"caption": "text", "hashtags": "text", "video_script": "video"}


def resolve_triples(variation_labels, variations):
    """Opción A: labels explícitos → cada uno con su directiva (single incluido).
    Sin labels → path viejo por count (n=1 sin directiva · n=3 con directivas)."""
    if variation_labels:
        return [(_BY_LABEL[lbl][0], lbl, _BY_LABEL[lbl][1]) for lbl in variation_labels]
    return _TEMP_TRIPLE if variations > 1 else _TEMP_SINGLE


async def generate_variations(
    system: str, request: GenerateTextRequest, dna: BrandDNA,
    client_id: str, triples: list, user_message: str,
) -> list[VariationItem]:
    coros = [
        generate(agent_code="content_creator", system=system,
                 messages=[{"role": "user", "content": _with_tone(user_message, directive)}],
                 max_tokens=1500, temperature=t)
        for t, _, directive in triples
    ]
    results = await asyncio.gather(*coros)

    out: list[VariationItem] = []
    for (resp, err), (temp, label, _) in zip(results, triples):
        if err or not resp:
            continue
        item = await _persist_variation(resp, temp, label, request, dna, client_id)
        if item:
            out.append(item)
    return out


def _with_tone(user_message: str, directive: str) -> str:
    """Appendea la directiva de tono al user_message (vacía en n=1 → sin cambio)."""
    return f"{user_message}\n\n{directive}" if directive else user_message


async def _persist_variation(
    resp: ClaudeResponse, temp: float, label: str,
    request: GenerateTextRequest, dna: BrandDNA, client_id: str,
) -> VariationItem | None:
    clean_text = extract_draft(resp.text)
    virality = compute_virality_score(clean_text, dna, request.platform)
    db_type = _UI_TO_DB_TYPE.get(request.content_type, "text")
    content_id = await repo.safe_insert(
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
    # DEBT-052: debita el costo real de Claude al cliente enrolado (best-effort)
    await debit(client_id, "content_creator", resp.cost_usd, resp.model_used, content_id)
    return VariationItem(
        id=content_id, label=label, temperature=temp,
        generated_text=clean_text, virality_score=virality["score"],
        virality_estimated=True, brand_dna_score=dna.score,
    )
