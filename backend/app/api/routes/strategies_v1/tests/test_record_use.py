"""ARCO MEDICION CAPA 1 Commit 1 · POST /strategies/{id}/use + repo record_use + last_used en list.
Estilo monkeypatch + asyncio.run (igual que test_strategies_generate_handler.py). Ownership en el WHERE
(client_ids) → 404 sin fuga. Opcion (ii): mark_used=true escribe estado=used; false deja estado intacto."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.api.routes.strategies_v1.handlers import record_use as ru
from app.bc_cognition.infrastructure import strategy_repository as strat


def _upd(sb):
    return sb.client.table.return_value.update.return_value.eq.return_value.in_.return_value.execute


def _list(sb):
    return (sb.client.table.return_value.select.return_value.in_.return_value
            .eq.return_value.order.return_value.limit.return_value.execute)


def test_use_completa():
    """mark_used=True → last_used + estado='used' + used_at (boton 'Usar' · va a Usadas)."""
    sb = MagicMock(); _upd(sb).return_value.data = [{"id": "s1"}]
    lu = {"platform": "completa", "brief": "b", "at": "2026-06-29T00:00:00+00:00"}
    assert strat.record_use(sb, "s1", lu, True, ["biz1"]) == 1
    patch = sb.client.table.return_value.update.call_args.args[0]
    assert patch["last_used"] == lu and patch["estado"] == "used" and "used_at" in patch
    sb.client.table.return_value.update.return_value.eq.return_value.in_.assert_called_with("client_id", ["biz1"])


def test_use_flecha():
    """mark_used=False → solo last_used · estado INTACTO (la flecha · opcion ii · sigue en Activas)."""
    sb = MagicMock(); _upd(sb).return_value.data = [{"id": "s1"}]
    lu = {"platform": "instagram", "brief": "idea IG", "at": "2026-06-29T00:00:00+00:00"}
    strat.record_use(sb, "s1", lu, False, ["biz1"])
    patch = sb.client.table.return_value.update.call_args.args[0]
    assert patch["last_used"] == lu and "estado" not in patch and "used_at" not in patch


def test_reuso_sobreescribe():
    """Dos usos → last_used = el ultimo (columna · se sobreescribe, no acumula)."""
    sb = MagicMock(); _upd(sb).return_value.data = [{"id": "s1"}]
    strat.record_use(sb, "s1", {"platform": "instagram", "brief": "1", "at": "t1"}, False, ["biz1"])
    lu2 = {"platform": "tiktok", "brief": "2", "at": "t2"}
    strat.record_use(sb, "s1", lu2, False, ["biz1"])
    assert sb.client.table.return_value.update.call_args.args[0]["last_used"] == lu2


def test_use_sin_client_ids():
    """Sin clientes accesibles → 0 filas (no escribe · ownership defensivo)."""
    assert strat.record_use(MagicMock(), "s1", {"platform": "x", "brief": "y", "at": "t"}, True, []) == 0


def test_last_used_en_list():
    """GET /strategies/?estado= ya incluye last_used (select '*')."""
    sb = MagicMock(); _list(sb).return_value.data = [{"id": "s1", "last_used": {"platform": "instagram"}}]
    rows = strat.list_strategies(sb, ["biz1"], "used")
    assert rows[0]["last_used"]["platform"] == "instagram"
    sb.client.table.return_value.select.assert_called_with("*")


def test_list_vieja_null():
    """Estrategia sin usar → last_used null en el list (honesto · no rompe)."""
    sb = MagicMock(); _list(sb).return_value.data = [{"id": "s1", "last_used": None}]
    assert strat.list_strategies(sb, ["biz1"], "active")[0]["last_used"] is None


def _auth(monkeypatch, client_ids):
    monkeypatch.setattr(ru, "get_current_user", AsyncMock(return_value={"id": "u1"}))
    monkeypatch.setattr(ru.reader, "get_accessible_client_ids", lambda uid: client_ids)
    monkeypatch.setattr(ru, "get_supabase_service", lambda: MagicMock())


def test_use_handler_construye_last_used(monkeypatch):
    """El handler arma last_used {platform, brief, at}, pasa mark_used, y lo devuelve."""
    _auth(monkeypatch, ["biz1"]); cap = {}
    def _fake(sb, sid, last_used, mark_used, cids):
        cap.update(last_used=last_used, mark_used=mark_used, sid=sid, cids=cids); return 1
    monkeypatch.setattr(ru.strat, "record_use", _fake)
    out = asyncio.run(ru.record_use("s1", ru.UseBody(platform="completa", brief="b", mark_used=True), "auth"))
    assert cap["mark_used"] is True and cap["sid"] == "s1" and cap["cids"] == ["biz1"]
    assert cap["last_used"]["platform"] == "completa" and cap["last_used"]["brief"] == "b" and "at" in cap["last_used"]
    assert out["last_used"]["platform"] == "completa"


def test_use_ownership(monkeypatch):
    """Estrategia de otro client → repo 0 filas → 404 (sin fuga · patron update_status)."""
    _auth(monkeypatch, ["biz1"])
    monkeypatch.setattr(ru.strat, "record_use", lambda *a, **k: 0)
    with pytest.raises(HTTPException) as ei:
        asyncio.run(ru.record_use("otra", ru.UseBody(platform="instagram", brief="b", mark_used=False), "auth"))
    assert ei.value.status_code == 404
