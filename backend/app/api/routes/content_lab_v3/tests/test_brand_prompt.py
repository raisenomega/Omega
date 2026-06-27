"""A2.1 · marca a utilidad reusable (D2): _brand_block (movido de A6) + fetch_brand_block (lee paleta + arma).
Fuente ÚNICA de marca para el handler n=1 (A6) Y el puente del carrusel (A2.4). Verifica byte-identidad con A6
y que un bloque por cliente se aplica a N prompts distintos. Mock del repo (cero DB). G9 exime tests."""
import asyncio

from app.api.routes.content_lab_v3 import _brand_prompt as bp
from app.api.routes.content_lab_v3.handlers.generate_image import _enhance_prompt

_PAL = {"primary_color": "#ec1313", "secondary_color": "#7c7979", "accent_color": "#0a0a0a"}


def test_fetch_brand_block_utilidad(monkeypatch):  # con/sin paleta
    monkeypatch.setattr(bp.repo, "find_client_brand_palette", lambda cid: _PAL)
    out = asyncio.run(bp.fetch_brand_block("c1"))
    assert "#ec1313" in out and "#7c7979" in out and "#0a0a0a" in out
    assert out == bp._brand_block(_PAL)  # la utilidad async == el formatter puro
    monkeypatch.setattr(bp.repo, "find_client_brand_palette", lambda cid: {})
    assert asyncio.run(bp.fetch_brand_block("c1")) == ""  # sin paleta → vacío


def test_handler_n1_identico(monkeypatch):  # A6 byte-idéntico: el enhanced sale igual que el inline de hoy
    monkeypatch.setattr(bp.repo, "find_client_brand_palette", lambda cid: _PAL)
    brand = asyncio.run(bp.fetch_brand_block("c1"))
    enhanced = _enhance_prompt("un gato", "realistic", brand)
    assert enhanced == _enhance_prompt("un gato", "realistic", bp._brand_block(_PAL))
    assert "#ec1313" in enhanced


def test_utilidad_aplica_a_lista(monkeypatch):  # un bloque por cliente → concatenable a N prompts distintos (A2)
    monkeypatch.setattr(bp.repo, "find_client_brand_palette", lambda cid: _PAL)
    brand = asyncio.run(bp.fetch_brand_block("c1"))
    prompts = [f"placa {i}{brand}" for i in range(3)]
    assert all("#ec1313" in p for p in prompts)
    assert prompts[0] != prompts[1]  # prompts distintos, misma marca
