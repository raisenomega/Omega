"""Tests for voyage_adapter (DEBT-048) · deploy-safe embeddings.

voyageai NO está instalado en el venv local: el caso success inyecta un fake
en sys.modules para que el import lazy lo resuelva. Cada test resetea el
singleton _adapter porque get_voyage_adapter() lo cachea entre llamadas.
"""
import sys
import types

from app.bc_cognition.infrastructure import voyage_adapter as va


def _reset_singleton() -> None:
    va._adapter = None


def test_embed_texts_none_when_no_key(monkeypatch) -> None:
    """Sin VOYAGE_API_KEY → adapter no disponible → embed_texts retorna None."""
    _reset_singleton()
    monkeypatch.setattr(va.settings, "voyage_api_key", "")
    assert va.embed_texts(["hola"], "document") is None
    assert va.get_voyage_adapter() is None


def test_embed_texts_maps_client_result_to_vectors(monkeypatch) -> None:
    """Con key + SDK fake → mapea result.embeddings a list[list[float]]."""
    _reset_singleton()
    monkeypatch.setattr(va.settings, "voyage_api_key", "vk-test")

    captured: dict = {}

    class _FakeResult:
        embeddings = [(0.1, 0.2, 0.3)]

    class _FakeClient:
        def __init__(self, api_key: str) -> None:
            captured["api_key"] = api_key

        def embed(self, texts, model, input_type, output_dimension):
            captured.update(
                texts=texts, model=model,
                input_type=input_type, output_dimension=output_dimension,
            )
            return _FakeResult()

    fake_mod = types.ModuleType("voyageai")
    setattr(fake_mod, "Client", _FakeClient)
    monkeypatch.setitem(sys.modules, "voyageai", fake_mod)

    out = va.embed_texts(["hola mundo"], "query")
    assert out == [[0.1, 0.2, 0.3]]
    assert captured["api_key"] == "vk-test"
    assert captured["model"] == "voyage-3-large"
    assert captured["input_type"] == "query"
    assert captured["output_dimension"] == 1024
    _reset_singleton()


def test_embed_texts_none_on_api_error(monkeypatch) -> None:
    """Excepción del SDK durante embed → None (caller cae a fallback)."""
    _reset_singleton()
    monkeypatch.setattr(va.settings, "voyage_api_key", "vk-test")

    class _BoomClient:
        def __init__(self, api_key: str) -> None:
            pass

        def embed(self, *a, **k):
            raise RuntimeError("voyage api down")

    fake_mod = types.ModuleType("voyageai")
    setattr(fake_mod, "Client", _BoomClient)
    monkeypatch.setitem(sys.modules, "voyageai", fake_mod)

    assert va.embed_texts(["x"], "document") is None
    _reset_singleton()
