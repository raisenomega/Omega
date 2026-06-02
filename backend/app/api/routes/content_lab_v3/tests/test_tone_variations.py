"""Fix de tono + contrato Opción A (DEBT-TONO · G9 exime tests).
Preserva la red de ddeb779: las directivas A/B/C siguen verificándose en el user_message.
Suma: resolución por variation_labels, backward-compat por count, y validación 422."""
import asyncio
import importlib

import pytest
from pydantic import ValidationError

from app.api.routes.content_lab_v3.models.content_lab_models import GenerateTextRequest
from app.bc_cognition.domain.brand_dna import BrandDNA

var = importlib.import_module("app.api.routes.content_lab_v3.handlers._variations")
sb = importlib.import_module("app.api.routes.content_lab_v3.handlers._system_builder")


def _dna(score: float) -> BrandDNA:
    return BrandDNA(tone=["cercano"], keywords=[("oferta", 3)], avg_length_words=40,
                    top_post_excerpts=["post ejemplo"], corpus_size=10, score=score)


def _req(**kw) -> GenerateTextRequest:
    base = dict(platform="instagram", content_type="caption", topic="x", tone="casual")
    base.update(kw)
    return GenerateTextRequest(**base)


def _run(monkeypatch, labels, variations):
    captured = {}

    async def _fake(*, agent_code, system, messages, max_tokens, temperature):
        captured[round(temperature, 2)] = messages[0]["content"]
        return (None, "skip")  # err → _persist se saltea (no DB, no billing)

    monkeypatch.setattr(var, "generate", _fake)
    triples = var.resolve_triples(labels, variations)
    asyncio.run(var.generate_variations(
        "SYS", _req(variation_labels=labels, variations=variations),
        _dna(0.8), "c1", triples, "Tema: x"))
    return triples, captured


def test_label_A_injects_prudente(monkeypatch):            # Test 1
    triples, cap = _run(monkeypatch, ["A"], 1)
    assert len(triples) == 1 and "prudente" in cap[0.4]


def test_label_C_injects_audaz(monkeypatch):               # Test 2 (preserva ddeb779 + Filosofía A)
    _, cap = _run(monkeypatch, ["C"], 1)
    assert "audaz" in cap[0.9] and "provocador" in cap[0.9]
    assert "SOSTENIDO DE PRINCIPIO A FIN" in cap[0.9]      # Filosofía A · audaz sostenido


def test_three_labels_all_directives(monkeypatch):         # Test 3
    triples, cap = _run(monkeypatch, ["A", "B", "C"], 1)
    assert len(triples) == 3
    assert "prudente" in cap[0.4] and "equilibrado" in cap[0.7] and "audaz" in cap[0.9]


def test_backward_count3_ABC(monkeypatch):                 # Test 4 (backward compat)
    triples, cap = _run(monkeypatch, None, 3)
    assert [t[1] for t in triples] == ["A", "B", "C"] and "audaz" in cap[0.9]


def test_backward_count1_no_directive(monkeypatch):        # Test 5 (como antes)
    triples, cap = _run(monkeypatch, None, 1)
    assert triples == [(0.7, "A", "")] and cap[0.7] == "Tema: x"


def test_empty_labels_422():                               # Test 6
    with pytest.raises(ValidationError):
        _req(variation_labels=[])


def test_invalid_label_422():                              # Test 7
    with pytest.raises(ValidationError):
        _req(variation_labels=["X"])


def test_duplicate_labels_422():                           # Test 8
    with pytest.raises(ValidationError):
        _req(variation_labels=["A", "A"])


def test_system_hierarchy_reinforced():                    # Filosofía A · jerarquía 4 puntos + DNA v2
    system = sb.build_rafa_system(
        client={"name": "Acme", "industry": "retail"}, ctx={}, dna=_dna(0.8),
        platform="instagram", content_type="caption", tone="profesional")
    assert "Jerarquía:" in system
    assert "(4)" in system
    assert "NO suavices ni 'balancees'" in system
    assert "SOLO vocabulario, expresiones características" in system
    assert "el cliente en su versión audaz" in system
    assert "imitá explícitamente el estilo de los samples" not in system
