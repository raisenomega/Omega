"""Guard de respuesta Nano Banana (DEBT-IMAGE-ASYNC-GEN-TYPEERROR · G9 exime tests).
Gemini puede devolver candidates/content/parts None (block/empty). Antes: crash
'NoneType not iterable'. Ahora: sin crash · safety_block limpio · happy path intacto."""
import asyncio
import importlib
from types import SimpleNamespace

nb = importlib.import_module("app.bc_cognition.infrastructure.nano_banana_adapter")


def _client(resp):
    async def _gen(**kw):
        return resp
    return SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=_gen)))


def _resp(parts):
    return SimpleNamespace(candidates=[SimpleNamespace(content=SimpleNamespace(parts=parts))])


def _patch(monkeypatch, resp):
    monkeypatch.setattr(nb, "_get_client", lambda: _client(resp))
    monkeypatch.setattr(nb, "record_mcp_use", lambda *a, **k: None)   # no toca HERMES/DB
    # SDK google-genai mockeado · test hermético (no depende de la versión local)
    monkeypatch.setattr(nb, "types", SimpleNamespace(
        GenerateContentConfig=lambda **k: object(),
        ImageConfig=lambda **k: object(),
        Part=SimpleNamespace(from_bytes=lambda **k: object()),
    ))


def test_parts_none_no_crash(monkeypatch):            # el caso EXACTO del owner
    _patch(monkeypatch, _resp(None))
    resp, err = asyncio.run(nb.generate("un gato", aspect_ratio="1:1"))
    assert resp is None and err is not None and err.code == "safety_block"


def test_candidates_none_no_crash(monkeypatch):
    _patch(monkeypatch, SimpleNamespace(candidates=None))
    resp, err = asyncio.run(nb.generate("un gato", aspect_ratio="1:1"))
    assert resp is None and err.code == "safety_block"


def test_valid_part_returns_image(monkeypatch):       # happy path intacto
    part = SimpleNamespace(inline_data=SimpleNamespace(data=b"\x89PNG", mime_type="image/png"))
    _patch(monkeypatch, _resp([part]))
    resp, err = asyncio.run(nb.generate("un gato", aspect_ratio="1:1"))
    assert err is None and resp is not None and resp.image_b64
