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
    return (
        f"{CONTENT_CREATOR_SYSTEM_PROMPT}\n\n"
        f"{_client_context_block(name, industry, audience, platform, content_type, tone)}\n\n"
        f"{_brand_dna_block(dna)}"
    )


def _client_context_block(name, industry, audience, platform, content_type, tone) -> str:
    return (
        "# CONTEXTO DEL CLIENTE\n"
        f"Cliente: {name} ({industry})\n"
        f"Audiencia: {audience}\n"
        f"Plataforma destino: {platform}\n"
        f"Tipo de contenido: {content_type}\n"
        f"Tono solicitado: {tone}"
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
        "DNA confiable: imitá explícitamente el estilo de los samples." if dna.is_strong()
        else "DNA débil: cliente nuevo, no fuerces imitación." if dna.is_weak()
        else "DNA emergente: usá con cautela, mezclá con defaults."
    )
    return f"{header}\n{tone_line}\n{kw_line}\n{length_line}\nSamples top:\n{samples}\nGuidance: {guidance}"
