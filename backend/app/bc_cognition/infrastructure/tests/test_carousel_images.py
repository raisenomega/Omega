"""Pieza 1 · A2.2 · generación paralela TODO-O-NADA (D4) · G9 exime tests.
Adapter + Storage mockeados en _image_compat (donde vive _generate_one). Prueba la LÓGICA todo-o-nada
y el ORDEN; el rate limit ya se midió en vivo (0 429, 10.1s K=6). La URL deriva del prompt → el orden
se verifica independiente del tiempo de completado del gather."""
import asyncio
import base64

import pytest

from app.bc_cognition.infrastructure import _image_compat as ic
from app.bc_cognition.infrastructure import _carousel_images as cc
from app.bc_cognition.infrastructure._nano_banana_types import ImageResponse, ImageError


def _wire(monkeypatch, fail_prompt=None):
    """Mock: cada placa devuelve una imagen cuyo contenido ES el prompt → la URL = /{prompt}.png.
    fail_prompt → esa placa devuelve error (→ _generate_one lanza RuntimeError → gather propaga)."""
    async def _gen(prompt, route, reference_images_b64, aspect_ratio):
        if prompt == fail_prompt:
            return None, ImageError("api_error", "boom")
        b64 = base64.b64encode(prompt.encode()).decode("ascii")
        return ImageResponse(image_b64=b64, mime_type="image/png", model_used="m", latency_ms=1), None

    async def _up(image_bytes, mime_type, client_id=None):
        return f"https://s/{image_bytes.decode()}.png"  # image_bytes = b64decode = el prompt

    monkeypatch.setattr(ic, "_nano_banana_generate", _gen)
    monkeypatch.setattr(ic, "upload_image_bytes", _up)


def test_N_paralelo_N_urls(monkeypatch):
    """6 placas en paralelo (gather) → 6 URLs, una por prompt."""
    _wire(monkeypatch)
    prompts = [f"p{i}" for i in range(6)]
    urls = asyncio.run(cc.generate_carousel_images(prompts, client_id="c1"))
    assert len(urls) == 6
    assert set(urls) == {f"https://s/p{i}.png" for i in range(6)}


def test_una_falla_todo_falla(monkeypatch):
    """La placa #4 falla → gather (return_exceptions=False) propaga → NINGUNA URL, 0 parcial (P1 · D4)."""
    _wire(monkeypatch, fail_prompt="p4")
    prompts = [f"p{i}" for i in range(6)]
    with pytest.raises(RuntimeError):
        asyncio.run(cc.generate_carousel_images(prompts, client_id="c1"))


def test_orden_preservado(monkeypatch):
    """gather preserva el orden de entrada → urls[i] corresponde a prompts[i] (el carrusel depende del orden)."""
    _wire(monkeypatch)
    prompts = ["portada", "tip1", "tip2", "cierre", "cta"]
    urls = asyncio.run(cc.generate_carousel_images(prompts, client_id="c1"))
    assert urls == [f"https://s/{p}.png" for p in prompts]


def test_lista_1_funciona(monkeypatch):
    """Borde: 1 prompt → 1 URL (el wrapper sirve también para N=1)."""
    _wire(monkeypatch)
    urls = asyncio.run(cc.generate_carousel_images(["solo"], client_id="c1"))
    assert urls == ["https://s/solo.png"]
