"""A2.4 (parte B) · ensamblado del prompt, sanitización y D5. Separado de test_carousel_render por el
techo C4 (≤100L). Reusa _common/_req del hermano. G9 exime tests."""
import asyncio

import pytest
from pydantic import ValidationError

from app.api.routes.content_lab_v3.handlers import carousel_render as cr
from app.api.routes.content_lab_v3.models.content_lab_models import (
    CarouselSlide, GenerateCarouselRenderRequest,
)
from app.api.routes.content_lab_v3.tests.test_carousel_render import _common, _req


def test_ensamblado_prompt(monkeypatch):
    cap: dict = {}
    _common(monkeypatch, cap=cap)
    asyncio.run(cr.carousel_render(_req(3), None))
    for i, prompt in enumerate(cap["prompts"]):
        assert prompt.index(f"dark bg {i}") < prompt.index("#00fa3e") < prompt.index(f"texto {i}")  # orden
        assert 'render this exact text on the design: "texto' in prompt
    assert cap["size"] == "1024x1280"  # 4:5


def test_sanitiza_slides(monkeypatch):
    h = _common(monkeypatch)
    asyncio.run(cr.carousel_render(_req(4), None))
    assert h["san"] == 8  # 4 slides × (text + visual_note)


def test_D5_pydantic():
    base = [CarouselSlide(text=f"t{i}", visual_note=f"v{i}") for i in range(11)]
    for bad in (base[:2], base):  # <3 y >10 → 422 (Pydantic)
        with pytest.raises(ValidationError):
            GenerateCarouselRenderRequest(carousel_title="x", slides=bad)
