"""BUG 503 (11 jun) · _parse_score tolera la respuesta TRUNCADA de Haiku.

Causa real del 503 "Verificador no disponible": Haiku genera un array `reasons`
largo que excede max_tokens → la respuesta se TRUNCA mid-string → json.loads
falla → score_brand_voice devuelve err → 503. El `score` viene PRIMERO y
completo; el fallback por regex lo rescata aunque el resto esté truncado.
(Capturado en prod · caption afb9f578 'CLIENTE DESTACADO'.)"""
from app.bc_cognition.application.score_brand_voice import _parse_score

# Respuesta real truncada: score completo, array reasons cortado mid-string.
_TRUNCATED = '''```json
{
  "score": 0.35,
  "reasons": [
    "Tono demasiado formal y corporativo: falta energia conversacional",
    "Vocabulario inconsistente: usa 'HydroJet' en lugar de la marca",
    "Ausencia de emojis estrategicos con proposito",
    "Falta urgencia y CTA coloquial de la marca",
    "Estructura de testimonial generica",
    "Hasht'''


def test_json_truncado_rescata_el_score():
    out = _parse_score(_TRUNCATED)
    assert out is not None              # antes devolvia None → 503 de todo el bloque
    assert out["score"] == 0.35


def test_json_limpio_normal():
    out = _parse_score('{"score": 0.82, "reasons": ["ok", "bien"]}')
    assert out["score"] == 0.82
    assert out["reasons"] == ["ok", "bien"]


def test_score_se_clampa_a_0_1():
    assert _parse_score('{"score": 1.5}')["score"] == 1.0
    assert _parse_score('{"score": -0.2}')["score"] == 0.0


def test_sin_score_devuelve_none():
    assert _parse_score("no hay json aqui") is None
    assert _parse_score('{"reasons": ["x"]}') is None
