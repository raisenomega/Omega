"""Fix de tono por variación (DEBT-TONO · G9 exime tests).
Test 1 _variations: cada A/B/C inyecta su directiva en el USER MESSAGE (no solo C).
Test 2 _system_builder: jerarquía tono>DNA en el SYSTEM + DNA reescrito ya no ordena
copiar el tono de los samples. Todo string-check · sin red ni modelo."""
import asyncio
import importlib

from app.api.routes.content_lab_v3.models.content_lab_models import GenerateTextRequest
from app.bc_cognition.domain.brand_dna import BrandDNA

var = importlib.import_module("app.api.routes.content_lab_v3.handlers._variations")
sb = importlib.import_module("app.api.routes.content_lab_v3.handlers._system_builder")


def _dna(score: float) -> BrandDNA:
    return BrandDNA(tone=["cercano"], keywords=[("oferta", 3)], avg_length_words=40,
                    top_post_excerpts=["post ejemplo"], corpus_size=10, score=score)


def test_variations_inject_tone_directive_all_three(monkeypatch):
    captured = {}

    async def _fake_generate(*, agent_code, system, messages, max_tokens, temperature):
        captured[round(temperature, 2)] = messages[0]["content"]
        return (None, "skip")  # err → _persist se saltea (no DB, no billing)

    monkeypatch.setattr(var, "generate", _fake_generate)
    req = GenerateTextRequest(platform="instagram", content_type="caption",
                              topic="lanzamiento", tone="profesional", variations=3)
    asyncio.run(var.generate_variations(
        system="SYS", request=req, dna=_dna(0.8),
        client_id="c1", n=3, user_message="Tema: lanzamiento"))
    assert "prudente" in captured[0.4]                                  # A Conservadora
    assert "equilibrado" in captured[0.7]                               # B Balanceada
    assert "audaz" in captured[0.9] and "provocador" in captured[0.9]   # C Atrevida


def test_variations_single_no_directive(monkeypatch):
    captured = {}

    async def _fake_generate(*, agent_code, system, messages, max_tokens, temperature):
        captured[round(temperature, 2)] = messages[0]["content"]
        return (None, "skip")

    monkeypatch.setattr(var, "generate", _fake_generate)
    req = GenerateTextRequest(platform="instagram", content_type="caption",
                              topic="lanzamiento", tone="profesional", variations=1)
    asyncio.run(var.generate_variations(
        system="SYS", request=req, dna=_dna(0.8),
        client_id="c1", n=1, user_message="Tema: lanzamiento"))
    assert captured[0.7] == "Tema: lanzamiento"          # n=1 → user_message intacto
    assert "TONO DE ESTA VERSIÓN" not in captured[0.7]


def test_system_hierarchy_and_rewritten_dna():
    system = sb.build_rafa_system(
        client={"name": "Acme", "industry": "retail"}, ctx={}, dna=_dna(0.8),
        platform="instagram", content_type="caption", tone="profesional")
    assert "Jerarquía:" in system
    assert "el tono de esta versión manda" in system
    assert "el Brand DNA modula contenido/vocabulario/voz, NO el tono" in system
    assert "si chocan, gana el tono pedido" in system
    assert "el TONO lo manda la directiva, NO copies el tono" in system
    assert "imitá explícitamente el estilo de los samples" not in system  # frase vieja ausente
