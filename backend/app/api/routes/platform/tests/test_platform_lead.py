"""Tests del endpoint público POST /platform/lead (lead de plataforma).

Verifica el corazón de la seguridad: reseller_id forzado NULL, source forzado, audience
validada, honeypot no inserta, rate-limit dispara. Mockea create_lead (no toca DB real).
"""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

mod = importlib.import_module("app.api.routes.platform.router")
from app.models.platform_models import CreatePlatformLeadRequest


class _Req:
    def __init__(self, ip: str):
        self.headers = {"x-forwarded-for": ip}
        self.client = SimpleNamespace(host=ip)


def _svc(captured: list):
    async def create_lead(data: dict) -> dict:
        captured.append(data)
        return data
    return SimpleNamespace(create_lead=create_lead)


def _run(body, ip="9.9.9.9", captured=None, monkeypatch=None):
    monkeypatch.setattr(mod, "get_supabase_service", lambda: _svc(captured if captured is not None else []))
    return asyncio.run(mod.create_platform_lead(_Req(ip), body))


def test_forces_reseller_null_source_and_consent(monkeypatch):
    mod._hits.clear()
    captured: list = []
    body = CreatePlatformLeadRequest(name="Ana", email="ana@test.com", audience="reseller", message="hola")
    out = _run(body, ip="1.1.1.1", captured=captured, monkeypatch=monkeypatch)
    assert out.success is True
    row = captured[0]
    assert row["reseller_id"] is None
    assert row["audience"] == "reseller"
    assert row["source"] == "omega_landing"
    assert row["consent_given"] is True
    assert row["email"] == "ana@test.com"


def test_honeypot_skips_insert(monkeypatch):
    mod._hits.clear()
    captured: list = []
    body = CreatePlatformLeadRequest(name="Bot", email="bot@test.com", website="http://spam")
    out = _run(body, ip="2.2.2.2", captured=captured, monkeypatch=monkeypatch)
    assert out.success is True
    assert captured == []  # honeypot lleno → no inserta


def test_audience_invalida_rechazada_por_el_modelo():
    with pytest.raises(ValidationError):
        CreatePlatformLeadRequest(name="Eve", email="eve@test.com", audience="hacker")


def test_safe_source_d7():
    # válido (slug) se conserva · inválido/None → default (nunca 422 por source)
    assert mod._safe_source("agendar_demo") == "agendar_demo"
    assert mod._safe_source("black-friday-2026") == "black-friday-2026"
    assert mod._safe_source(None) == "omega_landing"
    assert mod._safe_source("") == "omega_landing"
    assert mod._safe_source("Con Espacios!") == "omega_landing"
    assert mod._safe_source("x" * 51) == "omega_landing"  # >50


def test_source_llega_al_insert(monkeypatch):
    mod._hits.clear()
    captured: list = []
    body = CreatePlatformLeadRequest(name="Ana", email="ana@test.com", source="agendar_demo")
    _run(body, ip="7.7.7.7", captured=captured, monkeypatch=monkeypatch)
    assert captured[0]["source"] == "agendar_demo"


def test_rate_limit_por_ip(monkeypatch):
    mod._hits.clear()
    captured: list = []
    body = CreatePlatformLeadRequest(name="Ana", email="ana@test.com")
    for _ in range(mod._MAX_PER_WINDOW):
        _run(body, ip="3.3.3.3", captured=captured, monkeypatch=monkeypatch)
    with pytest.raises(HTTPException) as exc:
        _run(body, ip="3.3.3.3", captured=captured, monkeypatch=monkeypatch)
    assert exc.value.status_code == 429
    assert len(captured) == mod._MAX_PER_WINDOW  # el 6º no insertó
