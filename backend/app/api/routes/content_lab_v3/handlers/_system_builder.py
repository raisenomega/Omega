"""System prompt builder · wraps RAFA persona con DNA + contexto cliente.

Llamado desde generate_text handler antes de anthropic_adapter.generate().
Output va al system block (cache_control ephemeral en el adapter · I3).
"""
from app.bc_cognition.domain.brand_dna import BrandDNA
from app.bc_cognition.domain.personas.content_creator import (
    CONTENT_CREATOR_SYSTEM_PROMPT,
)


def build_rafa_system(
    client: dict, ctx: dict, dna: BrandDNA,
    platform: str, content_type: str, tone: str,
) -> str:
    name = client.get("name") or "este cliente"
    industry = client.get("industry") or "su industria"
    audience = ctx.get("target_audience") or client.get("target_audience") or "su audiencia"
    parts = [
        CONTENT_CREATOR_SYSTEM_PROMPT,
        _tone_hierarchy_block(tone),
        _client_context_block(name, industry, audience, platform, content_type),
        _brand_dna_block(dna),
    ]
    # Documento permanente del cliente (DEBT-039 V2 · /clients/{id}/upload-context).
    # Inyectado SIEMPRE al system · diferente de DEBT-CL-020 que era per-request.
    uploaded = ctx.get("uploaded_context_text")
    if uploaded:
        parts.append(_uploaded_context_block(str(uploaded)))
    return "\n\n".join(parts)


def _uploaded_context_block(text: str) -> str:
    return (
        "# CONTEXTO PERMANENTE DEL CLIENTE (documento adjunto)\n"
        "El cliente subió este documento como referencia de identidad/voz/contexto. "
        "Tomalo como verdad operativa permanente.\n\n"
        f"{text}"
    )


def _client_context_block(name, industry, audience, platform, content_type) -> str:
    return (
        "# CONTEXTO DEL CLIENTE\n"
        f"Cliente: {name} ({industry})\n"
        f"Audiencia: {audience}\n"
        f"Plataforma destino: {platform}\n"
        f"Tipo de contenido: {content_type}"
    )


def _tone_hierarchy_block(tone: str) -> str:
    return (
        "# TONO SOLICITADO (PRIORIDAD MÁXIMA)\n"
        f"Tono base solicitado: {tone}\n"
        "Jerarquía:\n"
        "(1) el tono de esta versión manda — de principio a fin, no solo al inicio.\n"
        "(2) el Brand DNA modula contenido/vocabulario/voz, NO el tono.\n"
        "(3) si chocan, gana el tono pedido.\n"
        "(4) IMPORTANTE: NO suavices ni 'balancees' el tono para 'caber' en la voz "
        "del cliente. La voz del cliente se EXPRESA en el tono pedido, no lo modera."
    )


def _brand_dna_block(dna: BrandDNA) -> str:
    label = dna.confidence_label()
    header = f"# BRAND DNA (score: {dna.score:.2f} · {label} · corpus N={dna.corpus_size})"
    if dna.corpus_size == 0:
        return f"{header}\nSin corpus disponible. Usá defaults profesionales sin forzar imitación."
    tone_line = "Tono dominante: " + (", ".join(dna.tone) if dna.tone else "(sin tags)")
    kw_line = "Keywords frecuentes: " + (
        ", ".join(f"{w}({c})" for w, c in dna.keywords) if dna.keywords else "(ninguna)"
    )
    length_line = f"Longitud típica: {dna.avg_length_words} palabras"
    samples = "\n".join(f"  · {s}" for s in dna.top_post_excerpts) or "  (sin samples)"
    guidance = (
        "DNA confiable: extraé de los samples SOLO vocabulario, expresiones "
        "características y referencias culturales del cliente. El TONO (intensidad, "
        "audacia, energía) lo manda la directiva de esta versión — NUNCA copies el "
        "nivel de atrevimiento de los samples. Si los samples son mesurados y la "
        "directiva pide audaz, el resultado es 'el cliente en su versión audaz', "
        "no 'el cliente como siempre'." if dna.is_strong()
        else "DNA débil: cliente nuevo, no fuerces imitación." if dna.is_weak()
        else "DNA emergente: usá con cautela, mezclá con defaults."
    )
    return f"{header}\n{tone_line}\n{kw_line}\n{length_line}\nSamples top:\n{samples}\nGuidance: {guidance}"
