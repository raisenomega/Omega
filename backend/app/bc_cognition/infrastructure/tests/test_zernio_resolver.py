"""zernio_resolver · resolucion accountId por plataforma (FASE 2a · solo-un-negocio). G9 exime tests.
CASO CLAVE P2: 2+ cuentas misma plataforma → FALLA (no adivina). list_accounts mockeado (sin red real)."""
import asyncio

import pytest

from app.bc_cognition.infrastructure import zernio_resolver as zr


def _patch(monkeypatch, accounts):
    async def _fake():
        return accounts
    monkeypatch.setattr(zr, "list_accounts", _fake)


def test_una_cuenta_de_la_plataforma_devuelve_id(monkeypatch):
    _patch(monkeypatch, [{"_id": "fb1", "platform": "facebook"}, {"_id": "ig1", "platform": "instagram"}])
    assert asyncio.run(zr.resolve_account_id("facebook")) == "fb1"  # filtra por plataforma, ignora ig


def test_sin_cuenta_de_la_plataforma_falla(monkeypatch):
    _patch(monkeypatch, [{"_id": "ig1", "platform": "instagram"}])
    with pytest.raises(zr.ZernioAccountResolutionError):
        asyncio.run(zr.resolve_account_id("facebook"))


def test_dos_cuentas_misma_plataforma_falla_no_adivina(monkeypatch):
    # P2: ambiguo → FALLA CLARO · NUNCA elige una (publicar en cuenta equivocada = peor error · multi=2b)
    _patch(monkeypatch, [{"_id": "fb1", "platform": "facebook"}, {"_id": "fb2", "platform": "facebook"}])
    with pytest.raises(zr.ZernioAccountResolutionError):
        asyncio.run(zr.resolve_account_id("facebook"))


def test_mapeo_persistido_gana_sin_llamar_live(monkeypatch):
    # F5/2b · si el caller pasa el mapeo per-negocio, GANA · NO consulta Zernio (desambigua multi-negocio)
    called = {"n": 0}
    async def _fake():
        called["n"] += 1
        return [{"_id": "X1", "platform": "instagram"}, {"_id": "X2", "platform": "instagram"}]  # 2+ = ambiguo
    monkeypatch.setattr(zr, "list_accounts", _fake)
    assert asyncio.run(zr.resolve_account_id("instagram", "MAP1")) == "MAP1"
    assert called["n"] == 0  # ni siquiera llamó list_accounts (mapeo cortocircuita)


def test_sin_mapeo_cae_al_fallback_live(monkeypatch):
    # F5/2b · mapped=None → backward compat: resuelve en vivo (path 2a)
    _patch(monkeypatch, [{"_id": "ig1", "platform": "instagram"}])
    assert asyncio.run(zr.resolve_account_id("instagram", None)) == "ig1"
