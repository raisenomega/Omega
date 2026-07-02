"""Endpoints email + notify de leads (F6-corrección pieza 2/3). Verifica surfacing honesto del
email (503/502 · nunca éxito falso) + auto-nota, y notify (not_a_user honesto vs usuario→notifica)."""
import asyncio
import importlib
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

leads = importlib.import_module("app.api.routes.resellers.leads")
from app.models.reseller_models import EmailLeadRequest

LEAD = {"id": "l1", "email": "a@b.com", "name": "Ana", "reseller_id": None, "notes": ""}


def _base(monkeypatch, *, send_result=(True, None), uid=None, cap=None):
    async def gcu(auth):
        if not auth:
            raise HTTPException(status_code=401, detail="no auth")
        return {"id": "u1", "reseller_id": "r1"}
    async def iso(x):
        return True  # super_owner → pasa _authz_lead sobre lead de plataforma
    async def get_lead(lid):
        return LEAD
    async def upd(lid, updates):
        if cap is not None:
            cap["note"] = updates.get("notes")
    async def resolve(email):
        if cap is not None:
            cap["resolved"] = email
        return uid
    async def create_notif(u, t, ti, b):
        if cap is not None:
            cap["notif"] = (u, ti)
    async def snd(to, subj, txt):
        if cap is not None:
            cap["email"] = (to, subj)
        return send_result
    svc = SimpleNamespace(get_lead_by_id=get_lead, update_lead=upd, user_id_by_email=resolve, create_notification=create_notif)
    monkeypatch.setattr(leads, "get_current_user", gcu)
    monkeypatch.setattr(leads, "is_super_owner_id", iso)
    monkeypatch.setattr(leads, "get_supabase_service", lambda: svc)
    monkeypatch.setattr(leads, "send_email", snd)


def test_email_ok_auto_nota(monkeypatch):
    cap: dict = {}
    _base(monkeypatch, send_result=(True, None), cap=cap)
    out = asyncio.run(leads.email_lead("l1", EmailLeadRequest(subject="Hola", message="Msg"), "Bearer x"))
    assert out.success is True
    assert cap["email"] == ("a@b.com", "Hola")
    assert "Email enviado" in cap["note"]


def test_email_not_configured_503(monkeypatch):
    _base(monkeypatch, send_result=(False, "not_configured"))
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads.email_lead("l1", EmailLeadRequest(subject="s", message="m"), "Bearer x"))
    assert e.value.status_code == 503


def test_email_rejected_502_no_exito_falso(monkeypatch):
    _base(monkeypatch, send_result=(False, "domain not verified"))
    with pytest.raises(HTTPException) as e:
        asyncio.run(leads.email_lead("l1", EmailLeadRequest(subject="s", message="m"), "Bearer x"))
    assert e.value.status_code == 502


def test_notify_not_a_user_honesto(monkeypatch):
    cap: dict = {}
    _base(monkeypatch, uid=None, cap=cap)
    out = asyncio.run(leads.notify_lead("l1", "Bearer x"))
    assert out.data["notified"] is False and out.data["reason"] == "not_a_user"
    assert "notif" not in cap  # no notificó


def test_notify_usuario_notifica(monkeypatch):
    cap: dict = {}
    _base(monkeypatch, uid="user-9", cap=cap)
    out = asyncio.run(leads.notify_lead("l1", "Bearer x"))
    assert out.data["notified"] is True
    assert cap["notif"][0] == "user-9"
    assert "Notificado" in cap["note"]
