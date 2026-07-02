"""IDOR guards de leads (INCIDENTE-SEC-002 · cierre). Verifica el corazón del ownership:
super_owner ve todo, el owner ve SOLO su reseller, leads de plataforma (reseller_id NULL) solo
super_owner, y el no-autorizado a un lead single recibe 404 (no confirma el UUID)."""
import asyncio
import importlib

import pytest
from fastapi import HTTPException

leads = importlib.import_module("app.api.routes.resellers.leads")


def _patch(monkeypatch, is_so: bool, user=None):
    async def _gcu(auth):
        if not auth:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        return user or {"id": "u1", "reseller_id": "r1"}
    async def _iso(uid):
        return is_so
    monkeypatch.setattr(leads, "get_current_user", _gcu)
    monkeypatch.setattr(leads, "is_super_owner_id", _iso)


# ── _authz_reseller (list / create por reseller_id) ──────────────────────────
def test_reseller_sin_token_401(monkeypatch):
    _patch(monkeypatch, is_so=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads._authz_reseller(None, "r1"))
    assert e.value.status_code == 401


def test_reseller_owner_propio_ok(monkeypatch):
    _patch(monkeypatch, is_so=False, user={"id": "u1", "reseller_id": "r1"})
    asyncio.run(leads._authz_reseller("Bearer x", "r1"))  # no raise


def test_reseller_ajeno_403(monkeypatch):
    _patch(monkeypatch, is_so=False, user={"id": "u1", "reseller_id": "r1"})
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads._authz_reseller("Bearer x", "r2"))
    assert e.value.status_code == 403


def test_reseller_super_owner_ve_todo(monkeypatch):
    _patch(monkeypatch, is_so=True, user={"id": "u9", "reseller_id": "rX"})
    asyncio.run(leads._authz_reseller("Bearer x", "cualquier-reseller"))  # no raise


# ── _authz_lead (un lead ya fetcheado · no-autorizado → 404) ─────────────────
def test_lead_plataforma_solo_super_owner_404(monkeypatch):
    _patch(monkeypatch, is_so=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads._authz_lead({"id": "u1", "reseller_id": "r1"}, {"reseller_id": None}))
    assert e.value.status_code == 404


def test_lead_plataforma_super_owner_ok(monkeypatch):
    _patch(monkeypatch, is_so=True)
    asyncio.run(leads._authz_lead({"id": "u9", "reseller_id": "rX"}, {"reseller_id": None}))  # no raise


def test_lead_reseller_ajeno_404(monkeypatch):
    _patch(monkeypatch, is_so=False)
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads._authz_lead({"id": "u1", "reseller_id": "r1"}, {"reseller_id": "r2"}))
    assert e.value.status_code == 404


def test_lead_reseller_propio_ok(monkeypatch):
    _patch(monkeypatch, is_so=False)
    asyncio.run(leads._authz_lead({"id": "u1", "reseller_id": "r1"}, {"reseller_id": "r1"}))  # no raise


# ── DEBT-LEADS-QUALIFIED · API alineada con el CHECK de DB ───────────────────
def test_qualified_en_valid_statuses():
    assert "qualified" in leads.VALID_LEAD_STATUSES
