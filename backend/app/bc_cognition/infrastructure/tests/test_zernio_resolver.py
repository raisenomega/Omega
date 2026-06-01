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
