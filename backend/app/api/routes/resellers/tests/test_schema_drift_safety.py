"""Red de seguridad schema-drift reseller (DEBT-SCHEMA-DRIFT-RESELLER · Sprint 8).

Columnas que el código asumía (agency_name, omega_commission_rate,
monthly_revenue_reported, suspend_switch, ...) NO existen en la tabla real.
Estos tests simulan el schema REAL (claves ausentes) y verifican que los
endpoints degradan honesto: NO lanzan 500, devuelven defaults / fallback.
"""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

stats_mod = importlib.import_module("app.api.routes.resellers.handlers.get_reseller_stats")
billing_mod = importlib.import_module("app.api.routes.resellers.handlers.get_reseller_billing")
public_mod = importlib.import_module("app.api.routes.resellers.public")
admin_mod = importlib.import_module("app.api.routes.resellers.admin")


class _Q:
    """Query chainable: ignora select/eq/order/limit/single, devuelve data fija."""
    def __init__(self, data): self._data = data
    def __getattr__(self, _): return lambda *a, **k: self
    def single(self): return self
    def execute(self): return SimpleNamespace(data=self._data)


def _svc(tables):
    return SimpleNamespace(client=SimpleNamespace(table=lambda n: _Q(tables.get(n))))


def test_stats_degrada_sin_columnas_fantasma(monkeypatch):
    # fila real solo trae 'id' (SIN omega_commission_rate / monthly_revenue_reported)
    tables = {"resellers": {"id": "r1"},
              "clients": [{"status": "active", "plan": "basic"}]}
    monkeypatch.setattr(stats_mod, "get_supabase_service", lambda: _svc(tables))
    out = asyncio.run(stats_mod.handle_get_reseller_stats("r1"))
    assert out["mrr_generated"] == 0 and out["commission_earned"] == 0
    assert out["clients_total"] == 1


def test_billing_degrada_sin_columnas_fantasma(monkeypatch):
    tables = {"resellers": {"id": "r1", "plan": "basic", "stripe_customer_id": None}}
    monkeypatch.setattr(billing_mod, "get_supabase_service", lambda: _svc(tables))
    out = asyncio.run(billing_mod.handle_get_reseller_billing("r1"))
    assert out["subscription"] is None
    assert out["commission"]["rate"] == 30            # fallback honesto
    assert out["commission"]["estimated_monthly"] == 0


def test_public_slug_agency_name_fallback_a_name(monkeypatch):
    async def _by_slug(slug):                          # schema real: SIN agency_name
        return {"id": "r1", "slug": "acme", "name": "Acme Agency", "status": "active"}
    async def _branding(rid): return None
    svc = SimpleNamespace(get_reseller_by_slug=_by_slug, get_branding=_branding)
    monkeypatch.setattr(public_mod, "get_supabase_service", lambda: svc)
    resp = asyncio.run(public_mod.get_branding_by_slug("acme"))
    assert resp.success is True
    assert resp.data["reseller"]["agency_name"] == "Acme Agency"


def test_update_status_ignora_suspend_switch(monkeypatch):
    captured = {}
    async def _get(rid): return {"id": rid, "status": "active"}
    async def _update(rid, data): captured["data"] = data; return {"id": rid, **data}
    svc = SimpleNamespace(get_reseller=_get, update_reseller=_update)
    monkeypatch.setattr(admin_mod, "get_supabase_service", lambda: svc)
    # solo suspend_switch (fantasma) → sin cambios reales → no UPDATE
    only_switch = admin_mod.UpdateResellerStatusRequest(suspend_switch=True)
    resp = asyncio.run(admin_mod.update_reseller_status("r1", only_switch))
    assert resp.success is True and "data" not in captured
    # con status (real) → UPDATE solo con status, sin suspend_switch
    both = admin_mod.UpdateResellerStatusRequest(status="suspended", suspend_switch=True)
    asyncio.run(admin_mod.update_reseller_status("r1", both))
    assert captured["data"] == {"status": "suspended"}


def test_create_reseller_501_pending_sprint8(monkeypatch):
    monkeypatch.setattr(admin_mod.settings, "signup_enabled", True)
    async def _by_slug(slug): return None
    monkeypatch.setattr(admin_mod, "get_supabase_service",
                        lambda: SimpleNamespace(get_reseller_by_slug=_by_slug))
    req = admin_mod.CreateResellerRequest(slug="acme", agency_name="Acme",
                                          owner_email="a@b.com", owner_name="Owner Name")
    with pytest.raises(HTTPException) as e:
        asyncio.run(admin_mod.create_reseller(req))
    assert e.value.status_code == 501
    assert e.value.detail == "reseller_provisioning_pending_sprint8"
