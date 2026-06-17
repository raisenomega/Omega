"""TEMP · test del endpoint de captura headless (DEBT-ZERNIO-CAPTURE-ENDPOINT-TEMP).
Verifica el gate del token de UN SOLO USO + redacción/visibilidad. Se remueve junto al
endpoint al cerrar el experimento. G9 exime tests."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import _zernio_experiment as exp


def _client(monkeypatch, token: str) -> TestClient:
    if token:
        monkeypatch.setenv("ZERNIO_CAPTURE_TOKEN", token)
    else:
        monkeypatch.delenv("ZERNIO_CAPTURE_TOKEN", raising=False)
    exp._consumed.clear()
    app = FastAPI()
    app.include_router(exp.router)
    return TestClient(app)


def test_capture_sin_token_es_403(monkeypatch):
    r = _client(monkeypatch, "secreto-xyz").get("/zernio-experiment/capture")
    assert r.status_code == 403


def test_capture_token_incorrecto_es_403(monkeypatch):
    r = _client(monkeypatch, "secreto-xyz").get("/zernio-experiment/capture", params={"cap": "otro"})
    assert r.status_code == 403


def test_capture_env_vacio_es_inerte_403(monkeypatch):
    r = _client(monkeypatch, "").get("/zernio-experiment/capture", params={"cap": "cualquier"})
    assert r.status_code == 403


def test_capture_token_valido_muestra_params_y_es_single_use(monkeypatch):
    c = _client(monkeypatch, "secreto-xyz")
    r = c.get("/zernio-experiment/capture",
              params={"cap": "secreto-xyz", "step": "select_page", "tempToken": "abc123"})
    assert r.status_code == 200
    assert "select_page" in r.text and "abc123" in r.text  # valor completo SOLO en pantalla efímera
    # segundo uso del mismo token → 410 (single-use)
    r2 = c.get("/zernio-experiment/capture", params={"cap": "secreto-xyz"})
    assert r2.status_code == 410
