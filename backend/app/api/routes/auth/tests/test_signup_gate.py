"""Gate de signup (SIGNUP_ENABLED) · cierra /register Y /resellers/create.

Ambos crean cuentas vía service-role (bypasean el toggle de Supabase Auth) →
necesitan gate en código. Con SIGNUP_ENABLED=false (default prod) → 403
'signups_closed' ANTES de crear nada. Con true → pasa el gate (reabrir para
onboarding controlado). Test-first: estos fallan hasta que exista el field+gate."""
import asyncio

import pytest
from fastapi import HTTPException

from app.config import settings
from app.api.routes.auth.models import RegisterRequest
from app.api.routes.auth.register import register
from app.models.reseller_models import CreateResellerRequest
from app.api.routes.resellers.admin import create_reseller


def test_register_403_when_signup_disabled(monkeypatch):
    monkeypatch.setattr(settings, "signup_enabled", False)
    req = RegisterRequest(name="Test User", email="new@example.com",
                          password="password123", plan="basic")
    with pytest.raises(HTTPException) as e:
        asyncio.run(register(req))
    assert e.value.status_code == 403
    assert e.value.detail == "signups_closed"


def test_register_passes_gate_when_enabled(monkeypatch):
    """Flag on → pasa el gate y llega al check de email (email ya existe → 400),
    probando que NO se queda en el 403 del gate."""
    monkeypatch.setattr(settings, "signup_enabled", True)

    class _Q:
        def select(self, *a, **k): return self
        def eq(self, *a, **k): return self
        def execute(self): return type("R", (), {"data": [{"id": "x", "email": "new@example.com"}]})()

    class _Client:
        def table(self, _n): return _Q()

    monkeypatch.setattr("app.api.routes.auth.register.get_supabase_service",
                        lambda: type("S", (), {"client": _Client()})())
    req = RegisterRequest(name="Test User", email="new@example.com",
                          password="password123", plan="basic")
    with pytest.raises(HTTPException) as e:
        asyncio.run(register(req))
    assert e.value.status_code == 400  # email exists → pasó el gate (no 403 signups_closed)


def test_reseller_create_403_when_signup_disabled(monkeypatch):
    """Segunda puerta: /resellers/create crea clients role='reseller' vía service-role
    sin auth → debe quedar igual de cerrada por el gate."""
    monkeypatch.setattr(settings, "signup_enabled", False)
    req = CreateResellerRequest(slug="testagency", agency_name="Test Agency",
                                owner_email="owner@example.com", owner_name="Owner Name")
    with pytest.raises(HTTPException) as e:
        asyncio.run(create_reseller(req))
    assert e.value.status_code == 403
    assert e.value.detail == "signups_closed"
