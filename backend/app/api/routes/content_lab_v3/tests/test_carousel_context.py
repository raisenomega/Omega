"""Fix DEBT-CAROUSEL-THIN-CONTEXT · RAFA lee el contexto RICO del negocio para escribir el guion.
TEST-FIRST: hoy _build_user_message solo pasa niche/audiencia/tono/nombre → RED en business_what y cía.
Calidad de contexto, NO volumen (P1 · campos relevantes + truncado, no las 30 columnas). G9 exime tests."""
from types import SimpleNamespace

from app.api.routes.content_lab_v3 import _carousel_brain as cb
from app.api.routes.content_lab_v3 import _content_lab_repository as repo


def test_query_trae_campos_negocio(monkeypatch):
    cap: dict = {}

    class _Q:
        def select(self, cols): cap["cols"] = cols; return self
        def eq(self, *a, **k): return self
        def limit(self, n): return self
        def execute(self): return SimpleNamespace(data=[{}])

    monkeypatch.setattr(repo, "_sb", lambda: SimpleNamespace(table=lambda t: _Q()))
    repo.find_client_context("c1")
    for col in ("business_what", "business_diff", "business_to_whom", "content_themes",
                "avoided_topics", "avoided_words", "custom_instructions", "brand_voice", "primary_goal"):
        assert col in cap["cols"], f"falta {col} en el select"


def test_user_message_incluye_que_ofrece():
    msg = cb._build_user_message(
        "5 tips", {"business_what": "servicio de limpieza de zafacones", "client_name": "Zafacones Ramos"}, 5)
    assert "servicio de limpieza de zafacones" in msg
    assert "Qué ofrece" in msg


def test_user_message_incluye_diferenciador_audiencia_evitar():
    msg = cb._build_user_message("idea", {
        "business_diff": "recogido el mismo día",
        "business_to_whom": "residenciales y comercios",
        "avoided_topics": "política",
        "custom_instructions": "siempre incluir el teléfono",
    }, 4)
    assert "recogido el mismo día" in msg
    assert "residenciales y comercios" in msg
    assert "política" in msg
    assert "siempre incluir el teléfono" in msg


def test_jsonb_campos_se_formatean():
    msg = cb._build_user_message("idea", {
        "content_themes": ["limpieza", "reciclaje"],
        "avoided_words": ["barato"],
        "brand_voice": {"keywords": ["profesional", "confiable"]},
    }, 3)
    assert "limpieza, reciclaje" in msg
    assert "barato" in msg
    assert "profesional, confiable" in msg


def test_campos_vacios_no_rompen():
    msg = cb._build_user_message(
        "idea", {"business_what": None, "business_diff": "", "client_name": "X", "content_themes": []}, 3)
    assert "None" not in msg
    assert "Qué ofrece" not in msg       # vacío → omitido (no label huérfano)
    assert "Diferenciador" not in msg
    assert "Cliente: X" in msg


def test_no_infla_prompt():
    msg = cb._build_user_message("idea", {"business_what": "x" * 5000}, 3)
    assert len(msg) < 1000   # campo largo truncado · el prompt total no explota (~2000 tokens)
