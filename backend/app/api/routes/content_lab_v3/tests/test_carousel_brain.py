"""Pieza 1 · A1.2 · cerebro del carrusel: guion estructurado GARANTIZADO vía tool_choice forzado (A1.1).
Mock del adapter (cero Claude real). Verifica shape + las 3 capas de garantía (la 3a = backstop de código).
NO genera imágenes (eso es A2). G9 exime tests."""
import asyncio
from unittest.mock import MagicMock

import pytest

from app.api.routes.content_lab_v3 import _carousel_brain as cb
from app.api.routes.content_lab_v3.models.content_lab_models import GenerateCarouselScriptRequest


def _slide(t="Limpieza profesional", v="dark background, bold headline top-left, minimal shapes"):
    return {"order": 1, "slide_type": "punto", "text": t, "visual_note": v}


def _resp(slides, title="5 tips de zafacones"):
    block = MagicMock(); block.type = "tool_use"
    block.input = {"carousel_title": title, "slides": slides}
    r = MagicMock(); r.tool_calls = [block]
    return r


def _patch_gen(monkeypatch, resp=None, err=None, capture=None):
    async def _gen(**kwargs):
        if capture is not None:
            capture.update(kwargs)
        return resp, err
    monkeypatch.setattr(cb, "generate", _gen)


def test_guion_N_slides_con_visual_note(monkeypatch):
    _patch_gen(monkeypatch, resp=_resp([_slide() for _ in range(5)]))
    out = asyncio.run(cb.generate_carousel_script("idea", {}, 5))
    assert out["carousel_title"] == "5 tips de zafacones"
    assert len(out["slides"]) == 5
    assert all(str(s["visual_note"]).strip() for s in out["slides"])


def test_tool_choice_forzado(monkeypatch):  # ejercita A1.1 · garantía capa 1
    cap: dict = {}
    _patch_gen(monkeypatch, resp=_resp([_slide() for _ in range(3)]), capture=cap)
    asyncio.run(cb.generate_carousel_script("idea", {}, 3))
    assert cap["tool_choice"] == {"type": "tool", "name": "emit_carousel_script"}
    assert cap["tools"][0]["name"] == "emit_carousel_script"


def test_backstop_visual_note_vacio(monkeypatch):  # garantía capa 3 · P1
    _patch_gen(monkeypatch, resp=_resp([_slide(), _slide(), _slide(v="")]))
    with pytest.raises(cb.CarouselScriptError):
        asyncio.run(cb.generate_carousel_script("idea", {}, 3))


def test_backstop_pocas_slides(monkeypatch):  # < 3 → rechaza
    _patch_gen(monkeypatch, resp=_resp([_slide(), _slide()]))
    with pytest.raises(cb.CarouselScriptError):
        asyncio.run(cb.generate_carousel_script("idea", {}, 3))


def test_cap_10(monkeypatch):  # D5 · > 10 → recorte amable por código
    _patch_gen(monkeypatch, resp=_resp([_slide() for _ in range(12)]))
    out = asyncio.run(cb.generate_carousel_script("idea", {}, 10))
    assert len(out["slides"]) == 10


def test_request_idea_larga_sin_422():  # campo propio max 4000 · NO el prompt de imagen (2000)
    req = GenerateCarouselScriptRequest(idea="x" * 3000, client_id="c1")
    assert len(req.idea) == 3000
