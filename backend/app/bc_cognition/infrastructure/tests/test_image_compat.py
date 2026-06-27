"""Pieza 1 · A3 · motor de generación N (generate_images_compat) · G9 exime tests.
Adapter (_nano_banana_generate) + Storage (upload_image_bytes) MOCKEADOS · NO genera ni sube de verdad.
CRÍTICO: el motor manda UN prompt distinto por placa (la lista), NO el mismo N veces. El test 1 lo fija
capturando los prompts que llegan al adapter, en orden. Retrocompat: generate_image_compat (single) intacto."""
import asyncio
import base64

from app.bc_cognition.infrastructure import _image_compat as ic
from app.bc_cognition.infrastructure._nano_banana_types import ImageResponse

_IMG_B64 = base64.b64encode(b"fake-image-bytes").decode("ascii")  # base64 válido para b64decode


def _wire(monkeypatch):
    """Mockea adapter + Storage · captura los prompts que llegan al adapter (en orden) y las refs."""
    cap: dict = {"prompts": [], "refs": []}

    async def _fake_gen(prompt, route, reference_images_b64, aspect_ratio):
        cap["prompts"].append(prompt)
        cap["refs"].append(reference_images_b64)
        return ImageResponse(image_b64=_IMG_B64, mime_type="image/png", model_used="m", latency_ms=10), None

    monkeypatch.setattr(ic, "_nano_banana_generate", _fake_gen)
    up: dict = {"n": 0}

    async def _fake_upload(image_bytes, mime_type, client_id=None):
        up["n"] += 1
        return f"https://storage/img{up['n']}.png"

    monkeypatch.setattr(ic, "upload_image_bytes", _fake_upload)
    return cap


def test_N_prompts_distintos_N_imagenes(monkeypatch):
    """N prompts DISTINTOS → N imágenes, cada llamada al adapter con SU prompt en orden (NO [p1,p1,p1])."""
    cap = _wire(monkeypatch)
    urls = asyncio.run(ic.generate_images_compat(["p1", "p2", "p3"], client_id="c1"))
    assert cap["prompts"] == ["p1", "p2", "p3"]  # ← FIJA el bug del prompt-repetido: distinto por placa
    assert len(urls) == 3
    assert urls == ["https://storage/img1.png", "https://storage/img2.png", "https://storage/img3.png"]


def test_lista_de_1_identico_a_hoy(monkeypatch):
    """Retrocompat dura: generate_image_compat(prompt, n=1) → 1 imagen, comportamiento de hoy intacto."""
    cap = _wire(monkeypatch)
    urls = asyncio.run(ic.generate_image_compat(prompt="solo", n=1, client_id="c1"))
    assert len(urls) == 1 and cap["prompts"] == ["solo"]


def test_lista_vacia_defensivo(monkeypatch):
    """Lista vacía → [] (no-op defensivo · sin crash, sin IndexError, sin llamada al adapter)."""
    cap = _wire(monkeypatch)
    urls = asyncio.run(ic.generate_images_compat([], client_id="c1"))
    assert urls == [] and cap["prompts"] == []


def test_n_mayor_a_1_legacy_mismo_prompt(monkeypatch):
    """Legacy: generate_image_compat(prompt, n=3) sigue repitiendo el MISMO prompt 3× (comportamiento intacto)."""
    cap = _wire(monkeypatch)
    urls = asyncio.run(ic.generate_image_compat(prompt="x", n=3, client_id="c1"))
    assert len(urls) == 3 and cap["prompts"] == ["x", "x", "x"]
